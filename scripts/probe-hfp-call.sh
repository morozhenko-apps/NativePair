#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C

DEVICE="${NATIVEPAIR_DEVICE:-}"
RECIPIENT="${NATIVEPAIR_CALL_RECIPIENT:-}"
DO_DIAL=no
OBSERVE_SECONDS="${NATIVEPAIR_CALL_OBSERVE_SECONDS:-8}"
TELEPHONY_SERVICE="org.pipewire.Telephony"
TELEPHONY_MANAGER="/org/pipewire/Telephony"
HFP_AG_UUID="0000111f-0000-1000-8000-00805f9b34fb"

usage() {
  cat <<'EOF'
Usage:
  ./scripts/probe-hfp-call.sh
  ./scripts/probe-hfp-call.sh --dial

Environment:
  NATIVEPAIR_DEVICE                Paired phone Bluetooth address.
  NATIVEPAIR_CALL_RECIPIENT        Test destination, accepted characters: 0-9 + * # , A-D.
  NATIVEPAIR_CALL_OBSERVE_SECONDS  Seconds to observe call state before hangup (default 8).

Default mode is a no-call preflight. --dial places one real outgoing call through
PipeWire Telephony, observes creation of a call object, then invokes HangupAll.

The destination is never printed. The probe refuses to dial if any call object
already exists.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dial)
      DO_DIAL=yes
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ ! "$DEVICE" =~ ^([[:xdigit:]]{2}:){5}[[:xdigit:]]{2}$ ]]; then
  echo "Invalid or missing Bluetooth address. Set NATIVEPAIR_DEVICE first." >&2
  exit 2
fi

if [[ ! "$OBSERVE_SECONDS" =~ ^[1-9][0-9]*$ ]]; then
  echo "NATIVEPAIR_CALL_OBSERVE_SECONDS must be a positive integer." >&2
  exit 2
fi

if [[ "$DO_DIAL" == yes ]] &&
  [[ ! "$RECIPIENT" =~ ^[0-9+*#,A-D]{1,80}$ ]]; then
  echo "Invalid or missing call recipient. Set NATIVEPAIR_CALL_RECIPIENT first." >&2
  exit 2
fi

for command in bluetoothctl busctl grep head mktemp sleep seq timeout; do
  if ! command -v "$command" >/dev/null 2>&1; then
    echo "Required command is missing: $command" >&2
    exit 1
  fi
done

TMP_DIR="$(mktemp -d)"
DIAL_ACCEPTED=no
HANGUP_DONE=no
AG_PATH=""
MODEMS_REPLY="$TMP_DIR/modems.reply"
CALLS_REPLY="$TMP_DIR/calls.reply"
DIAL_REPLY="$TMP_DIR/dial.reply"
HANGUP_REPLY="$TMP_DIR/hangup.reply"

cleanup() {
  local status=$?

  if [[ "$DIAL_ACCEPTED" == yes && "$HANGUP_DONE" != yes && -n "$AG_PATH" ]]; then
    busctl --user call "$TELEPHONY_SERVICE" "$AG_PATH"       org.pipewire.Telephony.AudioGateway1 HangupAll >/dev/null 2>&1 || true
  fi

  rm -rf "$TMP_DIR"
  exit "$status"
}
trap cleanup EXIT INT TERM

bool_line() {
  printf '%s=%s\n' "$1" "$2"
}

echo "nativepair_hfp_call_probe_schema=1"
echo "personal_payload_printed=no"
echo "dial_requested=$DO_DIAL"

info="$(bluetoothctl info "$DEVICE" 2>/dev/null || true)"
if [[ -z "$info" ]] ||
  ! grep -Eq '^[[:space:]]*Paired:[[:space:]]+yes$' <<<"$info"; then
  bool_line device_ready no
  exit 1
fi
bool_line device_ready yes

if ! grep -Fqi "$HFP_AG_UUID" <<<"$info"; then
  bool_line advertised_hfp_ag no
  exit 1
fi
bool_line advertised_hfp_ag yes

set +e
timeout 20s bluetoothctl connect "$DEVICE" "$HFP_AG_UUID" >/dev/null 2>&1
CONNECT_STATUS=$?
set -e

if [[ $CONNECT_STATUS -eq 124 ]]; then
  echo "hfp_connect_result=timeout"
  exit 1
else
  echo "hfp_connect_result=attempted"
fi

for _ in $(seq 1 50); do
  if busctl --user call "$TELEPHONY_SERVICE" "$TELEPHONY_MANAGER"     org.ofono.Manager GetModems >"$MODEMS_REPLY" 2>/dev/null; then
    AG_PATH="$(
      {
        grep -oE '/org/pipewire/Telephony/ag[0-9]+' "$MODEMS_REPLY" || true
      } |
        head -n 1
    )"
    [[ -n "$AG_PATH" ]] && break
  fi
  sleep 0.1
done

if [[ -z "$AG_PATH" ]]; then
  bool_line hfp_session_established no
  exit 1
fi
bool_line hfp_session_established yes

if ! busctl --user introspect "$TELEPHONY_SERVICE" "$AG_PATH" 2>/dev/null |
  grep -Fq 'Dial'; then
  bool_line call_control_api_available no
  exit 1
fi
bool_line call_control_api_available yes

if ! busctl --user call "$TELEPHONY_SERVICE" "$AG_PATH"   org.ofono.VoiceCallManager GetCalls >"$CALLS_REPLY" 2>/dev/null; then
  bool_line call_state_query_succeeded no
  exit 1
fi
bool_line call_state_query_succeeded yes

if grep -qE '/org/pipewire/Telephony/ag[0-9]+/call[0-9]+' "$CALLS_REPLY"; then
  bool_line preexisting_call_present yes
  echo "probe_complete=blocked"
  echo "note=refusing_to_dial_while_a_call_object_already_exists"
  exit 1
fi
bool_line preexisting_call_present no

if [[ "$DO_DIAL" != yes ]]; then
  echo "actual_dial=no"
  echo "call_state_mutation_performed=no"
  echo "probe_complete=preflight"
  echo "note=rerun_with_--dial_only_after_explicitly_approving_a_real_call"
  exit 0
fi

echo "actual_dial=yes"

set +e
busctl --user call "$TELEPHONY_SERVICE" "$AG_PATH"   org.pipewire.Telephony.AudioGateway1 Dial s "$RECIPIENT" >"$DIAL_REPLY" 2>&1
DIAL_STATUS=$?
set -e

if [[ $DIAL_STATUS -ne 0 ]]; then
  echo "dial_call_accepted=no"
  echo "probe_complete=no"
  echo "call_error=dial_failed"
  exit 1
fi
echo "dial_call_accepted=yes"
DIAL_ACCEPTED=yes

CALL_SEEN=no
for _ in $(seq 1 "$((OBSERVE_SECONDS * 10))"); do
  if busctl --user call "$TELEPHONY_SERVICE" "$AG_PATH"     org.ofono.VoiceCallManager GetCalls >"$CALLS_REPLY" 2>/dev/null &&
    grep -qE '/org/pipewire/Telephony/ag[0-9]+/call[0-9]+' "$CALLS_REPLY"; then
    CALL_SEEN=yes
    break
  fi
  sleep 0.1
done

echo "call_object_observed=$CALL_SEEN"

set +e
busctl --user call "$TELEPHONY_SERVICE" "$AG_PATH"   org.pipewire.Telephony.AudioGateway1 HangupAll >"$HANGUP_REPLY" 2>&1
HANGUP_STATUS=$?
set -e

if [[ $HANGUP_STATUS -eq 0 ]]; then
  HANGUP_DONE=yes
  echo "hangup_all_accepted=yes"
else
  echo "hangup_all_accepted=no"
  echo "probe_complete=no"
  echo "call_error=hangup_failed"
  exit 1
fi

echo "call_state_mutation_performed=yes"

if [[ "$CALL_SEEN" == yes ]]; then
  echo "probe_complete=yes"
  echo "note=dial_and_hangup_completed_verify_remote_device_observed_one_short_call"
else
  echo "probe_complete=inconclusive"
  echo "note=dial_was_accepted_but_no_call_object_was_observed_before_hangup"
fi
