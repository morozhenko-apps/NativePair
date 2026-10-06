#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C

DEVICE="${NATIVEPAIR_DEVICE:-}"
EVENT_TIMEOUT="${NATIVEPAIR_EVENT_TIMEOUT:-60}"
CONNECT_TIMEOUT="${NATIVEPAIR_OBEX_TIMEOUT:-45}"

usage() {
  cat <<'EOF'
Usage:
  ./scripts/probe-map-events.sh

Set the phone once in the current shell:

  export NATIVEPAIR_DEVICE='AA:BB:CC:DD:EE:FF'

Optional wait window:

  NATIVEPAIR_EVENT_TIMEOUT=90 ./scripts/probe-map-events.sh

The probe keeps a MAP session open and waits for BlueZ to expose a new
org.bluez.obex.Message1 object. Trigger one incoming SMS during the wait window.

The script never prints Bluetooth addresses, phone aliases, sender/recipient
data, message subject/body, or the Message1 object path.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
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

for value_name in EVENT_TIMEOUT CONNECT_TIMEOUT; do
  value="${!value_name}"
  if [[ ! "$value" =~ ^[1-9][0-9]*$ ]]; then
    echo "$value_name must be a positive integer." >&2
    exit 2
  fi
done

for command in busctl bluetoothctl obexctl stdbuf mktemp; do
  if ! command -v "$command" >/dev/null 2>&1; then
    echo "Required command is missing: $command" >&2
    exit 1
  fi
done

echo "nativepair_map_event_probe_schema=1"
echo "personal_payload_printed=no"
echo "event_window_seconds=$EVENT_TIMEOUT"

if ! busctl --user list 2>/dev/null | awk '{print $1}' | grep -Fxq org.bluez.obex; then
  echo "obex_service_available=no"
  exit 1
fi
echo "obex_service_available=yes"

if ! bluetoothctl info "$DEVICE" 2>/dev/null | grep -Eq '^[[:space:]]*Paired:[[:space:]]+yes$'; then
  echo "device_paired=no"
  exit 1
fi
echo "device_paired=yes"

TMP_DIR="$(mktemp -d)"
OBEX_LOG="$TMP_DIR/obexctl.log"
OBEX_INPUT="$TMP_DIR/obexctl.in"
mkfifo "$OBEX_INPUT"

OBEX_PID=""
OBEX_FD=""

cleanup() {
  local status=$?

  if [[ -n "$OBEX_FD" ]]; then
    printf 'disconnect\nquit\n' >&"$OBEX_FD" 2>/dev/null || true
    exec {OBEX_FD}>&- 2>/dev/null || true
  fi

  if [[ -n "$OBEX_PID" ]] && kill -0 "$OBEX_PID" 2>/dev/null; then
    for _ in 1 2 3 4 5; do
      kill -0 "$OBEX_PID" 2>/dev/null || break
      sleep 0.1
    done
    kill "$OBEX_PID" 2>/dev/null || true
    wait "$OBEX_PID" 2>/dev/null || true
  fi

  rm -rf "$TMP_DIR"
  exit "$status"
}
trap cleanup EXIT INT TERM

stdbuf -oL -eL obexctl <"$OBEX_INPUT" >"$OBEX_LOG" 2>&1 &
OBEX_PID=$!
exec {OBEX_FD}>"$OBEX_INPUT"

wait_for_log() {
  local pattern="$1"
  local timeout_seconds="$2"
  local elapsed=0

  while (( elapsed < timeout_seconds * 10 )); do
    if grep -Eq "$pattern" "$OBEX_LOG" 2>/dev/null; then
      return 0
    fi
    if ! kill -0 "$OBEX_PID" 2>/dev/null; then
      return 1
    fi
    sleep 0.1
    ((elapsed += 1))
  done

  return 1
}

if ! wait_for_log 'Client .*/org/bluez/obex|\[NEW\].*Client' 5; then
  echo "obexctl_ready=no"
  exit 1
fi
echo "obexctl_ready=yes"

printf 'connect %s map\n' "$DEVICE" >&"$OBEX_FD"

if ! wait_for_log 'Connection successful|Failed to connect' "$CONNECT_TIMEOUT"; then
  echo "session_established=no"
  echo "session_error=timeout"
  exit 1
fi

if grep -Fq 'Failed to connect' "$OBEX_LOG"; then
  echo "session_established=no"
  echo "session_error=connect_failed"
  exit 1
fi

if ! wait_for_log 'MessageAccess /org/bluez/obex/client/session|\[NEW\].*MessageAccess' 2; then
  echo "session_established=no"
  echo "session_error=message_access_proxy_missing"
  exit 1
fi

echo "session_established=yes"
echo "notification_registration_managed_by_bluez=yes"
echo "waiting_for_new_message_event=yes"

baseline_count="$(
  grep -Ec '\[NEW\].*Message /org/bluez/obex/client/session[0-9]+/message[0-9]+' "$OBEX_LOG" 2>/dev/null || true
)"

elapsed=0
event_observed=no
while (( elapsed < EVENT_TIMEOUT * 10 )); do
  current_count="$(
    grep -Ec '\[NEW\].*Message /org/bluez/obex/client/session[0-9]+/message[0-9]+' "$OBEX_LOG" 2>/dev/null || true
  )"

  if (( current_count > baseline_count )); then
    event_observed=yes
    break
  fi

  if ! kill -0 "$OBEX_PID" 2>/dev/null; then
    echo "map_event_observed=no"
    echo "event_probe_complete=no"
    echo "event_error=obexctl_exited"
    exit 1
  fi

  sleep 0.1
  ((elapsed += 1))
done

echo "map_event_observed=$event_observed"

if [[ "$event_observed" == yes ]]; then
  echo "event_probe_complete=yes"
  echo "note=new_message_proxy_observed_without_reading_personal_properties"
else
  echo "event_probe_complete=inconclusive"
  echo "note=no_new_message_event_observed_within_window"
fi
