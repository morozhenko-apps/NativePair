#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C

DEVICE="${NATIVEPAIR_DEVICE:-}"
TARGET=""
CONNECT_TIMEOUT="${NATIVEPAIR_OBEX_TIMEOUT:-45}"

usage() {
  cat <<'EOF'
Usage:
  ./scripts/probe-obex-session.sh --target map
  ./scripts/probe-obex-session.sh --target pbap
  ./scripts/probe-obex-session.sh --device AA:BB:CC:DD:EE:FF --target map

Set NATIVEPAIR_DEVICE once to avoid repeating the address:

  export NATIVEPAIR_DEVICE='AA:BB:CC:DD:EE:FF'

An explicit --device argument overrides NATIVEPAIR_DEVICE.

The probe keeps one obexctl process alive for the full session lifetime,
then inspects the live session through D-Bus. It never prints the Bluetooth
address, phone name, session object path, or personal payload data.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --device)
      [[ $# -ge 2 ]] || { echo "--device requires a Bluetooth address." >&2; exit 2; }
      DEVICE="$2"
      shift 2
      ;;
    --target)
      [[ $# -ge 2 ]] || { echo "--target requires map or pbap." >&2; exit 2; }
      TARGET="$2"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument." >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ ! "$DEVICE" =~ ^([[:xdigit:]]{2}:){5}[[:xdigit:]]{2}$ ]]; then
  echo "Invalid or missing Bluetooth address. Set NATIVEPAIR_DEVICE or use --device." >&2
  exit 2
fi

if [[ ! "$CONNECT_TIMEOUT" =~ ^[1-9][0-9]{0,17}$ ]] || (( CONNECT_TIMEOUT > 922337203685477580 )); then
  echo "NATIVEPAIR_OBEX_TIMEOUT must be a positive integer." >&2
  exit 2
fi

case "$TARGET" in
  map)
    EXPECTED_INTERFACE="org.bluez.obex.MessageAccess1"
    EXPECTED_PROXY_LABEL="MessageAccess"
    EXPECTED_TARGET_UUID="00001132-0000-1000-8000-00805f9b34fb"
    ;;
  pbap)
    EXPECTED_INTERFACE="org.bluez.obex.PhonebookAccess1"
    EXPECTED_PROXY_LABEL="PhonebookAccess"
    EXPECTED_TARGET_UUID="0000112f-0000-1000-8000-00805f9b34fb"
    ;;
  *)
    echo "Invalid or missing target. Use map or pbap." >&2
    exit 2
    ;;
esac

for command in busctl bluetoothctl obexctl stdbuf mktemp; do
  if ! command -v "$command" >/dev/null 2>&1; then
    echo "Required command is missing: $command" >&2
    exit 1
  fi
done

echo "nativepair_obex_probe_schema=3"
echo "target=$TARGET"

if ! busctl --user list 2>/dev/null | awk '{print $1}' | grep -Fxq org.bluez.obex; then
  echo "obex_service_available=no"
  echo "session_created=no"
  exit 1
fi
echo "obex_service_available=yes"

if ! bluetoothctl info "$DEVICE" 2>/dev/null | grep -Eq '^[[:space:]]*Paired:[[:space:]]+yes$'; then
  echo "device_paired=no"
  echo "session_created=no"
  exit 1
fi
echo "device_paired=yes"

TMP_DIR="$(mktemp -d)"
OBEX_LOG="$TMP_DIR/obexctl.log"
OBEX_INPUT="$TMP_DIR/obexctl.in"

OBEX_PID=""
OBEX_FD=""
SESSION_PATH=""

cleanup() {
  local status=$?
  trap - EXIT INT TERM
  trap '' PIPE

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
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
mkfifo "$OBEX_INPUT"

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
  echo "session_created=no"
  exit 1
fi
echo "obexctl_ready=yes"

printf 'connect %s %s\n' "$DEVICE" "$TARGET" >&"$OBEX_FD"

if ! wait_for_log 'Connection successful|Failed to connect' "$CONNECT_TIMEOUT"; then
  echo "session_created=no"
  echo "error=OBEX connection timed out waiting for phone authorization"
  exit 1
fi

if grep -Fq 'Failed to connect' "$OBEX_LOG"; then
  echo "session_created=no"
  echo "error=connect_failed"
  exit 1
fi

SESSION_PATH="$(
  sed -nE 's/.*Session (\/org\/bluez\/obex\/client\/session[0-9]+).*/\1/p' "$OBEX_LOG" |
    tail -n 1
)"

if [[ -z "$SESSION_PATH" ]]; then
  echo "session_created=no"
  echo "error=Connection succeeded but obexctl did not expose a session object"
  exit 1
fi
echo "session_created=yes"

# The session is still owned by the live obexctl D-Bus connection here.
if busctl --user introspect   org.bluez.obex   "$SESSION_PATH"   org.bluez.obex.Session1 >/dev/null 2>&1; then
  echo "session_interface_present=yes"
else
  echo "session_interface_present=no"
  exit 1
fi

set +e
TARGET_PROPERTY="$(
  busctl --user get-property     org.bluez.obex     "$SESSION_PATH"     org.bluez.obex.Session1     Target 2>&1
)"
TARGET_STATUS=$?
set -e

if [[ $TARGET_STATUS -eq 0 ]]; then
  SESSION_TARGET_UUID="$(
    sed -n 's/^s "\([^"]*\)".*/\1/p' <<<"$TARGET_PROPERTY" |
      tr '[:upper:]' '[:lower:]'
  )"
  if [[ ! "$SESSION_TARGET_UUID" =~ ^[[:xdigit:]]{8}-[[:xdigit:]]{4}-[[:xdigit:]]{4}-[[:xdigit:]]{4}-[[:xdigit:]]{12}$ ]]; then
    SESSION_TARGET_UUID=""
  fi
  printf 'session_target_uuid=%s\n' "${SESSION_TARGET_UUID:-unknown}"
  if [[ "$SESSION_TARGET_UUID" == "$EXPECTED_TARGET_UUID" ]]; then
    echo "session_target_matches=yes"
  else
    echo "session_target_matches=no"
  fi
else
  echo "session_target_uuid=unavailable"
  echo "session_target_matches=no"
fi

if busctl --user introspect   org.bluez.obex   "$SESSION_PATH"   "$EXPECTED_INTERFACE" >/dev/null 2>&1; then
  echo "target_interface_present=yes"
else
  echo "target_interface_present=no"
fi

if wait_for_log "\[NEW\].*$EXPECTED_PROXY_LABEL|$EXPECTED_PROXY_LABEL /org/bluez/obex/client/session" 2; then
  echo "target_proxy_observed=yes"
else
  echo "target_proxy_observed=no"
fi

if busctl --user introspect   org.bluez.obex   "$SESSION_PATH"   "$EXPECTED_INTERFACE" >/dev/null 2>&1; then
  echo "session_established=yes"
  echo "note=session_success_is_not_read_path_support"
else
  echo "session_established=no"
  echo "note=create_session_succeeded_but_target_interface_missing"
  exit 1
fi
