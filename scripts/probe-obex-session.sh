#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C

DEVICE=""
TARGET=""

usage() {
  cat <<'EOF'
Usage:
  ./scripts/probe-obex-session.sh --device AA:BB:CC:DD:EE:FF --target map
  ./scripts/probe-obex-session.sh --device AA:BB:CC:DD:EE:FF --target pbap

Creates a temporary BlueZ OBEX session through D-Bus, checks that the
target-specific interface appears, then removes the session.

The output is privacy-safe and does not print the Bluetooth address.
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
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ ! "$DEVICE" =~ ^([[:xdigit:]]{2}:){5}[[:xdigit:]]{2}$ ]]; then
  echo "Invalid or missing Bluetooth address." >&2
  exit 2
fi

case "$TARGET" in
  map)
    EXPECTED_INTERFACE="org.bluez.obex.MessageAccess1"
    ;;
  pbap)
    EXPECTED_INTERFACE="org.bluez.obex.PhonebookAccess1"
    ;;
  *)
    echo "Invalid or missing target. Use map or pbap." >&2
    exit 2
    ;;
esac

for command in busctl bluetoothctl; do
  if ! command -v "$command" >/dev/null 2>&1; then
    echo "Required command is missing: $command" >&2
    exit 1
  fi
done

sanitize() {
  sed -e "s/$DEVICE/<redacted-device>/g"
}

echo "nativepair_obex_probe_schema=1"
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

set +e
CALL_OUTPUT="$(
  busctl --user call     org.bluez.obex     /org/bluez/obex     org.bluez.obex.Client1     CreateSession     'sa{sv}'     "$DEVICE"     1     Target s "$TARGET" 2>&1
)"
CALL_STATUS=$?
set -e

if [[ $CALL_STATUS -ne 0 ]]; then
  echo "session_created=no"
  printf 'error=%s\n' "$(printf '%s' "$CALL_OUTPUT" | sanitize | tr '\n' ' ' | tr -s ' ' | cut -c1-300)"
  exit 1
fi

SESSION_PATH="$(sed -n 's/^o "\([^"]*\)".*/\1/p' <<<"$CALL_OUTPUT")"
if [[ -z "$SESSION_PATH" ]]; then
  echo "session_created=no"
  echo "error=CreateSession returned an unexpected response"
  exit 1
fi

cleanup() {
  busctl --user call     org.bluez.obex     /org/bluez/obex     org.bluez.obex.Client1     RemoveSession     o "$SESSION_PATH" >/dev/null 2>&1 || true
}
trap cleanup EXIT

echo "session_created=yes"

set +e
INTROSPECTION="$(
  busctl --user introspect org.bluez.obex "$SESSION_PATH" 2>&1
)"
INTROSPECT_STATUS=$?
set -e

if [[ $INTROSPECT_STATUS -ne 0 ]]; then
  echo "session_introspection=no"
  printf 'error=%s\n' "$(printf '%s' "$INTROSPECTION" | sanitize | tr '\n' ' ' | tr -s ' ' | cut -c1-300)"
  exit 1
fi

echo "session_introspection=yes"

if grep -Fq "$EXPECTED_INTERFACE" <<<"$INTROSPECTION"; then
  echo "target_interface_present=yes"
else
  echo "target_interface_present=no"
  exit 1
fi

echo "session_removed_on_exit=yes"
echo "note=session_success_is_not_read_path_support"
