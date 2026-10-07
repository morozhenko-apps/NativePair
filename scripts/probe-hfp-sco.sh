#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C

DEVICE="${NATIVEPAIR_DEVICE:-}"
RECIPIENT="${NATIVEPAIR_CALL_RECIPIENT:-}"
DO_DIAL=no
CONNECT_TIMEOUT="${NATIVEPAIR_HFP_CONNECT_TIMEOUT:-20}"
STATE_TIMEOUT="${NATIVEPAIR_SCO_STATE_TIMEOUT:-15}"
CALL_ACTIVE_TIMEOUT="${NATIVEPAIR_CALL_ACTIVE_TIMEOUT:-30}"
HUMAN_WINDOW="${NATIVEPAIR_SCO_HUMAN_WINDOW:-20}"

TELEPHONY_SERVICE="org.pipewire.Telephony"
TELEPHONY_MANAGER="/org/pipewire/Telephony"
TRANSPORT_IFACE="org.pipewire.Telephony.AudioGatewayTransport1"
HFP_AG_IFACE="org.pipewire.Telephony.AudioGateway1"
HFP_AG_UUID="0000111f-0000-1000-8000-00805f9b34fb"

usage() {
  cat <<'EOF'
Usage:
  ./scripts/probe-hfp-sco.sh
  ./scripts/probe-hfp-sco.sh --dial

Environment:
  NATIVEPAIR_DEVICE               Paired phone Bluetooth address.
  NATIVEPAIR_CALL_RECIPIENT       Real test destination, kept private.
  NATIVEPAIR_HFP_CONNECT_TIMEOUT  HFP connect timeout in seconds (default 20).
  NATIVEPAIR_SCO_STATE_TIMEOUT    Condition wait limit for SCO activation (default 15).
  NATIVEPAIR_CALL_ACTIVE_TIMEOUT  Condition wait limit for remote answer (default 30).
  NATIVEPAIR_SCO_HUMAN_WINDOW     Human audio-check window after activation (default 20).

Default invocation is preflight only. --dial creates one real outgoing call,
activates the PipeWire Telephony SCO transport, verifies matching HFP source/sink
nodes, leaves a short human verification window, and then hangs up.

The destination, caller metadata, and audio payload are never printed or stored.
The probe refuses to run the real test when a call already exists or RejectSCO
is enabled. Any accepted test call is hung up during cleanup on error or signal.
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

for value_name in CONNECT_TIMEOUT STATE_TIMEOUT CALL_ACTIVE_TIMEOUT HUMAN_WINDOW; do
  value="${!value_name}"
  if [[ ! "$value" =~ ^[1-9][0-9]*$ ]]; then
    echo "$value_name must be a positive integer." >&2
    exit 2
  fi
done

if [[ "$DO_DIAL" == yes ]] &&
  [[ ! "$RECIPIENT" =~ ^[0-9+*#,A-D]{1,80}$ ]]; then
  echo "Invalid or missing call recipient. Set NATIVEPAIR_CALL_RECIPIENT first." >&2
  exit 2
fi

for command in bluetoothctl busctl cat grep head mktemp python3 pw-dump sed seq sleep timeout wpctl; do
  if ! command -v "$command" >/dev/null 2>&1; then
    echo "Required command is missing: $command" >&2
    exit 1
  fi
done

TMP_DIR="$(mktemp -d)"
CONNECT_LOG="$TMP_DIR/connect.log"
MODEMS_REPLY="$TMP_DIR/modems.reply"
CALLS_REPLY="$TMP_DIR/calls.reply"
REJECT_REPLY="$TMP_DIR/reject.reply"
STATE_REPLY="$TMP_DIR/state.reply"
DIAL_REPLY="$TMP_DIR/dial.reply"
ACTIVATE_REPLY="$TMP_DIR/activate.reply"
HANGUP_REPLY="$TMP_DIR/hangup.reply"
CALL_STATE_REPLY="$TMP_DIR/call-state.reply"
PW_DUMP="$TMP_DIR/pw-dump.json"
NODE_RESULT="$TMP_DIR/nodes.result"

AG_PATH=""
CALL_PATH=""
CALL_STATE=""
DIAL_ACCEPTED=no
HANGUP_DONE=no

cleanup() {
  local status=$?
  trap - EXIT INT TERM

  if [[ "$DIAL_ACCEPTED" == yes && "$HANGUP_DONE" != yes && -n "$AG_PATH" ]]; then
    busctl --user call "$TELEPHONY_SERVICE" "$AG_PATH"       "$HFP_AG_IFACE" HangupAll >/dev/null 2>&1 || true
  fi

  rm -rf "$TMP_DIR"
  exit "$status"
}
trap cleanup EXIT INT TERM

bool_line() {
  printf '%s=%s\n' "$1" "$2"
}

read_transport_state() {
  if ! busctl --user get-property "$TELEPHONY_SERVICE" "$AG_PATH"     "$TRANSPORT_IFACE" State >"$STATE_REPLY" 2>/dev/null; then
    return 1
  fi
  sed -nE 's/^s "(.*)"$/\1/p' "$STATE_REPLY"
}

refresh_call_snapshot() {
  CALL_PATH=""
  CALL_STATE=""

  if ! busctl --user call "$TELEPHONY_SERVICE" "$AG_PATH" \
    org.ofono.VoiceCallManager GetCalls >"$CALLS_REPLY" 2>/dev/null; then
    return 1
  fi

  CALL_PATH="$(
    {
      grep -oE '/org/pipewire/Telephony/ag[0-9]+/call[0-9]+' "$CALLS_REPLY" || true
    } |
      head -n 1
  )"

  if [[ -z "$CALL_PATH" ]]; then
    return 2
  fi

  for state in active dialing alerting incoming waiting held disconnected; do
    if grep -Eq "\"State\"[[:space:]]+s[[:space:]]+\"$state\"" "$CALLS_REPLY"; then
      CALL_STATE="$state"
      return 0
    fi
  done

  for iface in org.pipewire.Telephony.Call1 org.ofono.VoiceCall; do
    if busctl --user get-property "$TELEPHONY_SERVICE" "$CALL_PATH" \
      "$iface" State >"$CALL_STATE_REPLY" 2>/dev/null; then
      CALL_STATE="$(sed -nE 's/^s "(.*)"$/\1/p' "$CALL_STATE_REPLY")"
      if [[ -n "$CALL_STATE" ]]; then
        return 0
      fi
    fi
  done

  return 0
}

inspect_hfp_nodes() {
  if ! pw-dump >"$PW_DUMP" 2>/dev/null; then
    return 1
  fi

  python3 - "$PW_DUMP" "$DEVICE" >"$NODE_RESULT" <<'PY'
import json
import sys

path, device = sys.argv[1:3]
with open(path, "r", encoding="utf-8") as handle:
    data = json.load(handle)

count = 0
source = False
sink = False

for obj in data:
    if obj.get("type") != "PipeWire:Interface:Node":
        continue
    info = obj.get("info") or {}
    props = info.get("props") or {}
    if props.get("api.bluez5.address") != device:
        continue
    if props.get("api.bluez5.profile") != "headset-head-unit":
        continue

    count += 1
    media_class = props.get("media.class")
    if media_class == "Audio/Source":
        source = True
    elif media_class == "Audio/Sink":
        sink = True

print(f"hfp_node_count={count}")
print(f"hfp_source_node_present={'yes' if source else 'no'}")
print(f"hfp_sink_node_present={'yes' if sink else 'no'}")
print(f"hfp_nodes_ready={'yes' if count >= 2 and source and sink else 'no'}")
PY
}

echo "nativepair_hfp_sco_probe_schema=2"
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
timeout "${CONNECT_TIMEOUT}s" bluetoothctl connect "$DEVICE" "$HFP_AG_UUID" >"$CONNECT_LOG" 2>&1
CONNECT_STATUS=$?
set -e

if [[ $CONNECT_STATUS -eq 124 ]]; then
  echo "hfp_connect_result=timeout"
  exit 1
elif grep -Fq 'Connection successful' "$CONNECT_LOG"; then
  echo "hfp_connect_result=success"
elif grep -Eqi 'already connected|connected: yes' "$CONNECT_LOG"; then
  echo "hfp_connect_result=already_connected"
else
  echo "hfp_connect_result=not_confirmed"
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

if ! busctl --user call "$TELEPHONY_SERVICE" "$AG_PATH"   org.ofono.VoiceCallManager GetCalls >"$CALLS_REPLY" 2>/dev/null; then
  bool_line call_state_query_succeeded no
  exit 1
fi
bool_line call_state_query_succeeded yes

if grep -qE '/org/pipewire/Telephony/ag[0-9]+/call[0-9]+' "$CALLS_REPLY"; then
  bool_line preexisting_call_present yes
  echo "probe_complete=blocked"
  echo "note=refusing_sco_test_while_a_call_object_already_exists"
  exit 1
fi
bool_line preexisting_call_present no

if ! busctl --user introspect "$TELEPHONY_SERVICE" "$AG_PATH" 2>/dev/null |
  grep -Fq 'AudioGatewayTransport1'; then
  bool_line transport_interface_available no
  exit 1
fi
bool_line transport_interface_available yes

if ! busctl --user introspect "$TELEPHONY_SERVICE" "$AG_PATH" 2>/dev/null |
  grep -Fq 'Activate'; then
  bool_line transport_activate_api_available no
  exit 1
fi
bool_line transport_activate_api_available yes

if ! busctl --user get-property "$TELEPHONY_SERVICE" "$AG_PATH"   "$TRANSPORT_IFACE" RejectSCO >"$REJECT_REPLY" 2>/dev/null; then
  bool_line reject_sco_readable no
  exit 1
fi
bool_line reject_sco_readable yes

if grep -Fq 'b true' "$REJECT_REPLY"; then
  echo "reject_sco=yes"
  echo "probe_complete=blocked"
  echo "note=sco_activation_is_blocked_by_pipewire_policy"
  exit 1
elif grep -Fq 'b false' "$REJECT_REPLY"; then
  echo "reject_sco=no"
else
  echo "reject_sco=unknown"
  echo "probe_complete=inconclusive"
  exit 1
fi

INITIAL_STATE="$(read_transport_state || true)"
printf 'transport_state_initial=%s\n' "${INITIAL_STATE:-unknown}"

if [[ "$DO_DIAL" != yes ]]; then
  echo "actual_dial=no"
  echo "transport_activate_invoked=no"
  echo "audio_stream_opened=no"
  echo "probe_complete=preflight"
  echo "note=rerun_with_--dial_only_after_explicitly_approving_a_real_call_and_audio_test"
  exit 0
fi

echo "actual_dial=yes"

set +e
busctl --user call "$TELEPHONY_SERVICE" "$AG_PATH"   "$HFP_AG_IFACE" Dial s "$RECIPIENT" >"$DIAL_REPLY" 2>&1
DIAL_STATUS=$?
set -e

if [[ $DIAL_STATUS -ne 0 ]]; then
  echo "dial_call_accepted=no"
  echo "probe_complete=no"
  echo "sco_error=dial_failed"
  exit 1
fi
DIAL_ACCEPTED=yes
echo "dial_call_accepted=yes"

CALL_SEEN=no
for _ in $(seq 1 "$((STATE_TIMEOUT * 10))"); do
  if refresh_call_snapshot && [[ -n "$CALL_PATH" ]]; then
    CALL_SEEN=yes
    break
  fi
  sleep 0.1
done
echo "call_object_observed=$CALL_SEEN"

if [[ "$CALL_SEEN" != yes ]]; then
  echo "probe_complete=no"
  echo "sco_error=no_call_object"
  exit 1
fi

echo "awaiting_remote_answer=yes"
CALL_ACTIVE_SEEN=no
LAST_CALL_STATE=""
for _ in $(seq 1 "$((CALL_ACTIVE_TIMEOUT * 10))"); do
  if refresh_call_snapshot; then
    LAST_CALL_STATE="$CALL_STATE"
    if [[ "$LAST_CALL_STATE" == active ]]; then
      CALL_ACTIVE_SEEN=yes
      break
    fi
  fi
  sleep 0.1
done

printf 'call_state_before_activate=%s\n' "${LAST_CALL_STATE:-unknown}"
echo "call_active_observed=$CALL_ACTIVE_SEEN"

if [[ "$CALL_ACTIVE_SEEN" != yes ]]; then
  echo "probe_complete=no"
  echo "sco_error=call_not_active"
  exit 1
fi

set +e
busctl --user call "$TELEPHONY_SERVICE" "$AG_PATH"   "$TRANSPORT_IFACE" Activate >"$ACTIVATE_REPLY" 2>&1
ACTIVATE_STATUS=$?
set -e

if [[ $ACTIVATE_STATUS -ne 0 ]]; then
  echo "transport_activate_accepted=no"
  ACTIVATE_ERROR_CLASS="$(
    {
      grep -oE 'org\.pipewire\.Telephony\.Error\.(InvalidState|NotSupported|InProgress|Failed|CME)|org\.freedesktop\.DBus\.Error\.(InvalidArgs|Failed)' "$ACTIVATE_REPLY" ||
        true
    } |
      head -n 1
  )"
  printf 'activate_error_class=%s\n' "${ACTIVATE_ERROR_CLASS:-unknown}"
  echo "probe_complete=no"
  echo "sco_error=activate_failed"
  exit 1
fi
echo "transport_activate_accepted=yes"

ACTIVE_SEEN=no
LAST_STATE=""
for _ in $(seq 1 "$((STATE_TIMEOUT * 10))"); do
  LAST_STATE="$(read_transport_state || true)"
  if [[ "$LAST_STATE" == active ]]; then
    ACTIVE_SEEN=yes
    break
  fi
  sleep 0.1
done

printf 'transport_state_after_activate=%s\n' "${LAST_STATE:-unknown}"
echo "transport_active_observed=$ACTIVE_SEEN"

if [[ "$ACTIVE_SEEN" != yes ]]; then
  echo "probe_complete=no"
  echo "sco_error=transport_not_active"
  exit 1
fi

NODES_READY=no
for _ in $(seq 1 "$((STATE_TIMEOUT * 10))"); do
  if inspect_hfp_nodes && grep -Fq 'hfp_nodes_ready=yes' "$NODE_RESULT"; then
    NODES_READY=yes
    break
  fi
  sleep 0.1
done

if [[ -s "$NODE_RESULT" ]]; then
  cat "$NODE_RESULT"
else
  echo "hfp_node_count=unknown"
  echo "hfp_source_node_present=unknown"
  echo "hfp_sink_node_present=unknown"
  echo "hfp_nodes_ready=no"
fi

echo "pipewire_hfp_nodes_observed=$NODES_READY"

if [[ "$NODES_READY" != yes ]]; then
  echo "probe_complete=no"
  echo "sco_error=hfp_nodes_not_ready"
  exit 1
fi

echo "human_audio_check_window_seconds=$HUMAN_WINDOW"
echo "human_audio_check_required=yes"
sleep "$HUMAN_WINDOW"

set +e
busctl --user call "$TELEPHONY_SERVICE" "$AG_PATH"   "$HFP_AG_IFACE" HangupAll >"$HANGUP_REPLY" 2>&1
HANGUP_STATUS=$?
set -e

if [[ $HANGUP_STATUS -ne 0 ]]; then
  echo "hangup_all_accepted=no"
  echo "probe_complete=no"
  echo "sco_error=hangup_failed"
  exit 1
fi

HANGUP_DONE=yes
echo "hangup_all_accepted=yes"
echo "probe_complete=yes"
echo "note=sco_transport_and_pipewire_nodes_proven_human_bidirectional_audio_confirmation_required"
