#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C

DEVICE="${NATIVEPAIR_DEVICE:-}"
TARGET=""

usage() {
  cat <<'EOF'
Usage:
  ./scripts/probe-obex-session.sh --target map
  ./scripts/probe-obex-session.sh --target pbap
  ./scripts/probe-obex-session.sh --device AA:BB:CC:DD:EE:FF --target map

Set NATIVEPAIR_DEVICE once to avoid repeating the address:

  export NATIVEPAIR_DEVICE='AA:BB:CC:DD:EE:FF'

An explicit --device argument overrides NATIVEPAIR_DEVICE.

Creates a temporary BlueZ OBEX session through D-Bus, records only
privacy-safe session metadata, then removes the session.

The output never prints the Bluetooth address or session object path.
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
  echo "Invalid or missing Bluetooth address. Set NATIVEPAIR_DEVICE or use --device." >&2
  exit 2
fi

case "$TARGET" in
  map)
    EXPECTED_INTERFACE="org.bluez.obex.MessageAccess1"
    EXPECTED_TARGET_UUID="00001132-0000-1000-8000-00805f9b34fb"
    ;;
  pbap)
    EXPECTED_INTERFACE="org.bluez.obex.PhonebookAccess1"
    EXPECTED_TARGET_UUID="0000112f-0000-1000-8000-00805f9b34fb"
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

compact_error() {
  sanitize | tr '\n' ' ' | tr -s ' ' | cut -c1-300
}

echo "nativepair_obex_probe_schema=2"
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
  printf 'error=%s\n' "$(printf '%s' "$CALL_OUTPUT" | compact_error)"
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
TARGET_PROPERTY="$(
  busctl --user get-property     org.bluez.obex     "$SESSION_PATH"     org.bluez.obex.Session1     Target 2>&1
)"
TARGET_STATUS=$?
set -e

if [[ $TARGET_STATUS -eq 0 ]]; then
  SESSION_TARGET_UUID="$(sed -n 's/^s "\([^"]*\)".*/\1/p' <<<"$TARGET_PROPERTY" | tr '[:upper:]' '[:lower:]')"
  printf 'session_target_uuid=%s\n' "${SESSION_TARGET_UUID:-unknown}"
  if [[ "$SESSION_TARGET_UUID" == "$EXPECTED_TARGET_UUID" ]]; then
    echo "session_target_matches=yes"
  else
    echo "session_target_matches=no"
  fi
else
  echo "session_target_uuid=unavailable"
  echo "session_target_matches=no"
  printf 'target_property_error=%s\n' "$(printf '%s' "$TARGET_PROPERTY" | compact_error)"
fi

set +e
INTROSPECTION="$(
  busctl --user introspect org.bluez.obex "$SESSION_PATH" 2>&1
)"
INTROSPECT_STATUS=$?
set -e

if [[ $INTROSPECT_STATUS -ne 0 ]]; then
  echo "session_introspection=no"
  printf 'error=%s\n' "$(printf '%s' "$INTROSPECTION" | compact_error)"
  exit 1
fi

echo "session_introspection=yes"

SESSION_INTERFACES="$(
  awk '$2 == "interface" { print $1 }' <<<"$INTROSPECTION" |
    sort -u |
    paste -sd, -
)"
printf 'session_interfaces=%s\n' "${SESSION_INTERFACES:-none}"

if grep -Fq "$EXPECTED_INTERFACE" <<<"$INTROSPECTION"; then
  echo "target_interface_present=yes"
else
  echo "target_interface_present=no"
  echo "session_removed_on_exit=yes"
  echo "note=session_created_but_target_interface_missing"
  exit 1
fi

echo "session_removed_on_exit=yes"
echo "note=session_success_is_not_read_path_support"
