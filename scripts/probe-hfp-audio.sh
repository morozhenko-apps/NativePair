#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C

DEVICE="${NATIVEPAIR_DEVICE:-}"
CONNECT_TIMEOUT="${NATIVEPAIR_HFP_CONNECT_TIMEOUT:-20}"
TELEPHONY_SERVICE="org.pipewire.Telephony"
TELEPHONY_MANAGER="/org/pipewire/Telephony"
TRANSPORT_IFACE="org.pipewire.Telephony.AudioGatewayTransport1"
HFP_AG_UUID="0000111f-0000-1000-8000-00805f9b34fb"

usage() {
  cat <<'EOF'
Usage:
  ./scripts/probe-hfp-audio.sh

Environment:
  NATIVEPAIR_DEVICE               Paired phone Bluetooth address.
  NATIVEPAIR_HFP_CONNECT_TIMEOUT  HFP profile connect timeout in seconds (default 20).

This is a privacy-safe HFP audio transport preflight. It connects to the phone's
remote HFP Audio Gateway and inspects PipeWire Telephony transport capabilities.

It never places a call, never invokes AudioGatewayTransport1.Activate, never
opens an audio stream, and never prints phone numbers or caller metadata.
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

for command in awk bluetoothctl busctl grep head mktemp sed seq sleep timeout; do
  if ! command -v "$command" >/dev/null 2>&1; then
    echo "Required command is missing: $command" >&2
    exit 1
  fi
done

TMP_DIR="$(mktemp -d)"
CONNECT_LOG="$TMP_DIR/connect.log"
MODEMS_REPLY="$TMP_DIR/modems.reply"
AG_INTROSPECT="$TMP_DIR/ag.introspect"
STATE_REPLY="$TMP_DIR/state.reply"
CODEC_REPLY="$TMP_DIR/codec.reply"
REJECT_REPLY="$TMP_DIR/reject.reply"

cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

bool_line() {
  printf '%s=%s\n' "$1" "$2"
}

echo "nativepair_hfp_audio_probe_schema=1"
echo "personal_payload_printed=no"
echo "call_performed=no"
echo "transport_activate_invoked=no"
echo "audio_stream_opened=no"

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

set +e
timeout "${CONNECT_TIMEOUT}s" bluetoothctl connect "$DEVICE" "$HFP_AG_UUID" >"$CONNECT_LOG" 2>&1
CONNECT_STATUS=$?
set -e

if [[ $CONNECT_STATUS -eq 124 ]]; then
  echo "hfp_profile_connect_result=timeout"
  exit 1
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
    [[ -n "$AG_PATH" ]] && break
  fi
  sleep 0.1
done

if [[ -z "$AG_PATH" ]]; then
  bool_line hfp_session_established no
  exit 1
fi
bool_line hfp_session_established yes

if ! busctl --user introspect "$TELEPHONY_SERVICE" "$AG_PATH" >"$AG_INTROSPECT" 2>/dev/null; then
  bool_line transport_interface_available no
  exit 1
fi

if grep -Fq "$TRANSPORT_IFACE" "$AG_INTROSPECT"; then
  bool_line transport_interface_available yes
else
  bool_line transport_interface_available no
  exit 1
fi

if grep -Fq 'Activate' "$AG_INTROSPECT"; then
  bool_line transport_activate_api_available yes
else
  bool_line transport_activate_api_available no
fi

if busctl --user get-property "$TELEPHONY_SERVICE" "$AG_PATH"   "$TRANSPORT_IFACE" State >"$STATE_REPLY" 2>/dev/null; then
  bool_line transport_state_readable yes
else
  bool_line transport_state_readable no
  exit 1
fi

if busctl --user get-property "$TELEPHONY_SERVICE" "$AG_PATH"   "$TRANSPORT_IFACE" Codec >"$CODEC_REPLY" 2>/dev/null; then
  bool_line transport_codec_readable yes
else
  bool_line transport_codec_readable no
  exit 1
fi

if busctl --user get-property "$TELEPHONY_SERVICE" "$AG_PATH"   "$TRANSPORT_IFACE" RejectSCO >"$REJECT_REPLY" 2>/dev/null; then
  bool_line reject_sco_readable yes
else
  bool_line reject_sco_readable no
  exit 1
fi

STATE="$(sed -nE 's/^s "(idle|pending|active|error)"$/\1/p' "$STATE_REPLY")"
CODEC="$(sed -nE 's/^y ([0-9]+)$/\1/p' "$CODEC_REPLY")"
REJECT_SCO="$(sed -nE 's/^b (true|false)$/\1/p' "$REJECT_REPLY")"

printf 'transport_state=%s\n' "${STATE:-unknown}"
printf 'transport_codec_id=%s\n' "${CODEC:-unknown}"

case "${CODEC:-}" in
  1) echo "transport_codec=cvsd" ;;
  2) echo "transport_codec=msbc" ;;
  3) echo "transport_codec=lc3_swb" ;;
  *) echo "transport_codec=unknown" ;;
esac

case "${REJECT_SCO:-}" in
  true)
    echo "reject_sco=yes"
    echo "sco_activation_blocked=yes"
    ;;
  false)
    echo "reject_sco=no"
    echo "sco_activation_blocked=no"
    ;;
  *)
    echo "reject_sco=unknown"
    echo "sco_activation_blocked=unknown"
    ;;
esac

if [[ -n "$STATE" && -n "$CODEC" && -n "$REJECT_SCO" ]]; then
  echo "probe_complete=yes"
  echo "note=transport_preflight_only_no_call_no_activate_no_audio_stream"
else
  echo "probe_complete=inconclusive"
  echo "note=transport_interface_present_but_one_or_more_properties_could_not_be_parsed"
fi
