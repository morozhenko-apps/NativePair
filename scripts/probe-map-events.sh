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

The probe starts a low-level D-Bus monitor before creating the MAP session,
observes the short-lived notification-registration Transfer1 object, then
waits for BlueZ to expose a new org.bluez.obex.Message1 object.

Trigger one incoming SMS during the wait window.

Raw D-Bus and obexctl output is stored only in a temporary directory and
deleted on exit. The script never prints Bluetooth addresses, phone aliases,
sender/recipient data, message subject/body, or OBEX object paths.
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

echo "nativepair_map_event_probe_schema=3"
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

if bluetoothctl show 2>/dev/null |
  tr '[:upper:]' '[:lower:]' |
  grep -Fq '00001133-0000-1000-8000-00805f9b34fb'; then
  echo "local_mns_profile_advertised=yes"
else
  echo "local_mns_profile_advertised=no"
fi

TMP_DIR="$(mktemp -d)"
OBEX_LOG="$TMP_DIR/obexctl.log"
MONITOR_LOG="$TMP_DIR/busctl-monitor.log"
OBEX_INPUT="$TMP_DIR/obexctl.in"
mkfifo "$OBEX_INPUT"

OBEX_PID=""
OBEX_FD=""
MONITOR_PID=""
SESSION_PATH=""

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

  if [[ -n "$MONITOR_PID" ]] && kill -0 "$MONITOR_PID" 2>/dev/null; then
    kill "$MONITOR_PID" 2>/dev/null || true
    wait "$MONITOR_PID" 2>/dev/null || true
  fi

  rm -rf "$TMP_DIR"
  exit "$status"
}
trap cleanup EXIT INT TERM

# Transfer1 can be created and removed before obexctl publishes a proxy for it.
# Start the monitor before the MAP session so that short lifetime is observable.
stdbuf -oL -eL busctl --user monitor org.bluez.obex >"$MONITOR_LOG" 2>&1 &
MONITOR_PID=$!
sleep 0.3

if ! kill -0 "$MONITOR_PID" 2>/dev/null; then
  echo "dbus_monitor_ready=no"
  exit 1
fi
echo "dbus_monitor_ready=yes"

stdbuf -oL -eL obexctl <"$OBEX_INPUT" >"$OBEX_LOG" 2>&1 &
OBEX_PID=$!
exec {OBEX_FD}>"$OBEX_INPUT"

wait_for_log() {
  local file="$1"
  local pattern="$2"
  local timeout_seconds="$3"
  local elapsed=0

  while (( elapsed < timeout_seconds * 10 )); do
    if grep -Eq "$pattern" "$file" 2>/dev/null; then
      return 0
    fi
    sleep 0.1
    ((elapsed += 1))
  done

  return 1
}

if ! wait_for_log "$OBEX_LOG" 'Client .*/org/bluez/obex|\[NEW\].*Client' 5; then
  echo "obexctl_ready=no"
  exit 1
fi
echo "obexctl_ready=yes"

printf 'connect %s map\n' "$DEVICE" >&"$OBEX_FD"

if ! wait_for_log "$OBEX_LOG" 'Connection successful|Failed to connect' "$CONNECT_TIMEOUT"; then
  echo "session_established=no"
  echo "session_error=timeout"
  exit 1
fi

if grep -Fq 'Failed to connect' "$OBEX_LOG"; then
  echo "session_established=no"
  echo "session_error=connect_failed"
  exit 1
fi

SESSION_PATH="$(
  sed -nE 's/.*Session (\/org\/bluez\/obex\/client\/session[0-9]+).*/\1/p' "$OBEX_LOG" |
    tail -n 1
)"

if [[ -z "$SESSION_PATH" ]]; then
  echo "session_established=no"
  echo "session_error=session_object_missing"
  exit 1
fi

if ! wait_for_log "$OBEX_LOG" 'MessageAccess /org/bluez/obex/client/session|\[NEW\].*MessageAccess' 2; then
  echo "session_established=no"
  echo "session_error=message_access_proxy_missing"
  exit 1
fi

echo "session_established=yes"
echo "notification_registration_attempted_by_bluez=yes"

registration_transfer_seen=no
registration_transfer_status=not_seen

if wait_for_log "$MONITOR_LOG" 'org\.bluez\.obex\.Transfer1' 3; then
  registration_transfer_seen=yes

  for _ in {1..30}; do
    if grep -Eqi 'Status.*complete|complete.*Status' "$MONITOR_LOG"; then
      registration_transfer_status=complete
      break
    fi
    if grep -Eqi 'Status.*error|error.*Status' "$MONITOR_LOG"; then
      registration_transfer_status=error
      break
    fi
    sleep 0.1
  done

  if [[ "$registration_transfer_status" == not_seen ]]; then
    registration_transfer_status=unknown
  fi
fi

echo "notification_registration_transfer_seen=$registration_transfer_seen"
echo "notification_registration_status=$registration_transfer_status"

echo "waiting_for_new_message_event=yes"

baseline_monitor_messages="$(
  grep -Ec 'org\.bluez\.obex\.Message1' "$MONITOR_LOG" 2>/dev/null || true
)"
baseline_obexctl_messages="$(
  grep -Ec '\[NEW\].*Message /org/bluez/obex/client/session[0-9]+/message[0-9]+' "$OBEX_LOG" 2>/dev/null || true
)"

elapsed=0
event_observed=no
while (( elapsed < EVENT_TIMEOUT * 10 )); do
  current_monitor_messages="$(
    grep -Ec 'org\.bluez\.obex\.Message1' "$MONITOR_LOG" 2>/dev/null || true
  )"
  current_obexctl_messages="$(
    grep -Ec '\[NEW\].*Message /org/bluez/obex/client/session[0-9]+/message[0-9]+' "$OBEX_LOG" 2>/dev/null || true
  )"

  if (( current_monitor_messages > baseline_monitor_messages ||
        current_obexctl_messages > baseline_obexctl_messages )); then
    event_observed=yes
    break
  fi

  if ! kill -0 "$OBEX_PID" 2>/dev/null; then
    echo "map_event_observed=no"
    echo "event_probe_complete=no"
    echo "event_error=obexctl_exited"
    exit 1
  fi

  if ! kill -0 "$MONITOR_PID" 2>/dev/null; then
    echo "map_event_observed=no"
    echo "event_probe_complete=no"
    echo "event_error=dbus_monitor_exited"
    exit 1
  fi

  sleep 0.1
  ((elapsed += 1))
done

echo "map_event_observed=$event_observed"

if [[ "$event_observed" == yes ]]; then
  echo "notification_registration_effective=yes"
  echo "event_probe_complete=yes"
  if [[ "$registration_transfer_status" == complete ]]; then
    echo "note=new_message_proxy_observed_and_registration_completion_seen"
  else
    echo "note=new_message_proxy_observed_so_registration_was_effective_even_without_explicit_completion_status"
  fi
else
  echo "event_probe_complete=inconclusive"
  if [[ "$registration_transfer_status" != complete ]]; then
    echo "note=no_event_and_notification_registration_not_proven"
  else
    echo "note=registration_completed_but_no_new_message_event_observed_within_window"
  fi
fi
