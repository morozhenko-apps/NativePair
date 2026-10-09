#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C

DEVICE="${NATIVEPAIR_DEVICE:-}"
CONNECT_TIMEOUT="${NATIVEPAIR_HFP_CONNECT_TIMEOUT:-20}"
TELEPHONY_SERVICE="org.pipewire.Telephony"
TELEPHONY_MANAGER="/org/pipewire/Telephony"
HFP_AG_UUID="0000111f-0000-1000-8000-00805f9b34fb"

usage() {
  cat <<'EOF'
Usage:
  ./scripts/probe-hfp.sh

Environment:
  NATIVEPAIR_DEVICE               Paired phone Bluetooth address.
  NATIVEPAIR_HFP_CONNECT_TIMEOUT  HFP profile connect timeout in seconds (default 20).

The probe may establish the HFP Hands-Free profile connection to the paired phone.
It never dials, answers, hangs up, sends DTMF, or prints caller/phone-number data.
EOF
}

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  usage
  exit 0
fi

if [[ $# -ne 0 ]]; then
  echo "Unknown argument." >&2
  usage >&2
  exit 2
fi

if [[ ! "$DEVICE" =~ ^([[:xdigit:]]{2}:){5}[[:xdigit:]]{2}$ ]]; then
  echo "Invalid or missing Bluetooth address. Set NATIVEPAIR_DEVICE first." >&2
  exit 2
fi

if [[ ! "$CONNECT_TIMEOUT" =~ ^[1-9][0-9]{0,17}$ ]] || (( CONNECT_TIMEOUT > 922337203685477580 )); then
  echo "NATIVEPAIR_HFP_CONNECT_TIMEOUT must be a positive integer." >&2
  exit 2
fi

for command in bluetoothctl busctl grep awk sed head tail tr mktemp timeout seq sleep; do
  if ! command -v "$command" >/dev/null 2>&1; then
    echo "Required command is missing: $command" >&2
    exit 1
  fi
done

TMP_DIR="$(mktemp -d)"
CONNECT_LOG="$TMP_DIR/hfp-connect.log"
MANAGER_INTROSPECT="$TMP_DIR/manager.introspect"
MODEMS_REPLY="$TMP_DIR/modems.reply"
AG_INTROSPECT="$TMP_DIR/ag.introspect"
CALLS_REPLY="$TMP_DIR/calls.reply"
PW_DUMP="$TMP_DIR/pw-dump.json"

cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

bool_line() {
  printf '%s=%s\n' "$1" "$2"
}

echo "nativepair_hfp_probe_schema=1"
echo "personal_payload_printed=no"
echo "outgoing_call_performed=no"
echo "call_control_mutation_performed=no"

info="$(bluetoothctl info "$DEVICE" 2>/dev/null || true)"
if [[ -z "$info" ]]; then
  bool_line device_visible no
  exit 1
fi
bool_line device_visible yes

if grep -Eq '^[[:space:]]*Paired:[[:space:]]+yes$' <<<"$info"; then
  bool_line device_paired yes
else
  bool_line device_paired no
  exit 1
fi

if grep -Fqi "$HFP_AG_UUID" <<<"$info"; then
  bool_line advertised_hfp_ag yes
else
  bool_line advertised_hfp_ag no
  exit 1
fi

if command -v systemctl >/dev/null 2>&1 &&
  systemctl --user is-active --quiet pipewire.service 2>/dev/null; then
  bool_line pipewire_service_active yes
else
  bool_line pipewire_service_active no
fi

if command -v systemctl >/dev/null 2>&1 &&
  systemctl --user is-active --quiet wireplumber.service 2>/dev/null; then
  bool_line wireplumber_service_active yes
else
  bool_line wireplumber_service_active no
fi

if command -v pipewire >/dev/null 2>&1; then
  pipewire_version="$(pipewire --version 2>/dev/null | tail -n 1 | tr -cd '[:alnum:].:_ -')"
  printf 'pipewire_version=%s\n' "${pipewire_version:-unknown}"
else
  echo "pipewire_version=unavailable"
fi

if command -v wireplumber >/dev/null 2>&1; then
  wireplumber_version="$(wireplumber --version 2>/dev/null | tail -n 1 | tr -cd '[:alnum:].:_ -')"
  printf 'wireplumber_version=%s\n' "${wireplumber_version:-unknown}"
else
  echo "wireplumber_version=unavailable"
fi

if busctl --user introspect "$TELEPHONY_SERVICE" "$TELEPHONY_MANAGER" >"$MANAGER_INTROSPECT" 2>/dev/null; then
  bool_line telephony_service_available yes
else
  bool_line telephony_service_available no
fi

if grep -Fq 'org.ofono.Manager' "$MANAGER_INTROSPECT" 2>/dev/null &&
  grep -Fq 'GetModems' "$MANAGER_INTROSPECT" 2>/dev/null; then
  bool_line telephony_manager_api_available yes
else
  bool_line telephony_manager_api_available no
fi

# The phone is the remote HFP Audio Gateway (UUID 0x111f). Connecting to that
# remote service makes PipeWire's local role HFP Hands-Free. Do not target the
# remote HFP-HF UUID here; that reverses the roles.
echo "remote_hfp_service=hfp_ag"
set +e
timeout "${CONNECT_TIMEOUT}s" bluetoothctl connect "$DEVICE" "$HFP_AG_UUID" >"$CONNECT_LOG" 2>&1
CONNECT_STATUS=$?
set -e

if [[ $CONNECT_STATUS -eq 124 ]]; then
  echo "hfp_profile_connect_result=timeout"
elif grep -Fq 'Connection successful' "$CONNECT_LOG"; then
  echo "hfp_profile_connect_result=success"
elif grep -Eqi 'already connected|connected: yes' "$CONNECT_LOG"; then
  echo "hfp_profile_connect_result=already_connected"
else
  echo "hfp_profile_connect_result=not_confirmed"
fi

AG_PATH=""
for _ in $(seq 1 50); do
  if busctl --user call "$TELEPHONY_SERVICE" "$TELEPHONY_MANAGER"     org.ofono.Manager GetModems >"$MODEMS_REPLY" 2>/dev/null; then
    AG_PATH="$(awk -F'"' '
      { for (i = 2; i <= NF; i += 2) if ($i ~ /^\/org\/pipewire\/Telephony\/ag[0-9]+$/) seen[$i] = 1 }
      END { for (path in seen) { count++; last = path } if (count == 1) print last }
    ' "$MODEMS_REPLY")"
    if [[ -n "$AG_PATH" ]]; then
      break
    fi
  fi
  sleep 0.1
done

if [[ -n "$AG_PATH" ]]; then
  bool_line telephony_audio_gateway_present yes
  bool_line hfp_session_established yes
else
  bool_line telephony_audio_gateway_present no
  bool_line hfp_session_established no
fi

if [[ -n "$AG_PATH" ]] &&
  busctl --user introspect "$TELEPHONY_SERVICE" "$AG_PATH" >"$AG_INTROSPECT" 2>/dev/null; then
  if grep -Fq 'org.pipewire.Telephony.AudioGateway1' "$AG_INTROSPECT" &&
    grep -Fq 'Dial' "$AG_INTROSPECT" &&
    grep -Fq 'HangupAll' "$AG_INTROSPECT" &&
    grep -Fq 'SendTones' "$AG_INTROSPECT"; then
    bool_line call_control_api_available yes
  else
    bool_line call_control_api_available no
  fi

  if grep -Fq 'org.ofono.VoiceCallManager' "$AG_INTROSPECT" &&
    grep -Fq 'GetCalls' "$AG_INTROSPECT"; then
    bool_line call_state_api_available yes
  else
    bool_line call_state_api_available no
  fi
else
  bool_line call_control_api_available no
  bool_line call_state_api_available no
fi

if [[ -n "$AG_PATH" ]] &&
  busctl --user call "$TELEPHONY_SERVICE" "$AG_PATH"     org.ofono.VoiceCallManager GetCalls >"$CALLS_REPLY" 2>/dev/null; then
  bool_line call_state_query_succeeded yes
  if grep -qE '/org/pipewire/Telephony/ag[0-9]+/call[0-9]+' "$CALLS_REPLY"; then
    bool_line call_objects_present yes
  else
    bool_line call_objects_present no
  fi
else
  bool_line call_state_query_succeeded no
  bool_line call_objects_present unknown
fi

if command -v pw-dump >/dev/null 2>&1 &&
  pw-dump >"$PW_DUMP" 2>/dev/null; then
  if grep -Fqi "$DEVICE" "$PW_DUMP"; then
    bool_line pipewire_bluez_device_present yes
  else
    bool_line pipewire_bluez_device_present no
  fi
else
  bool_line pipewire_bluez_device_present unknown
fi

echo "audio_stream_test_performed=no"
echo "probe_complete=yes"
echo "note=no_call_was_created_or_modified"
