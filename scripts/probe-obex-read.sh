#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C

DEVICE="${NATIVEPAIR_DEVICE:-}"
TARGET=""
CONNECT_TIMEOUT="${NATIVEPAIR_OBEX_TIMEOUT:-45}"

usage() {
  cat <<'EOF'
Usage:
  ./scripts/probe-obex-read.sh --target map
  ./scripts/probe-obex-read.sh --target pbap

Set the phone once in the current shell:

  export NATIVEPAIR_DEVICE='AA:BB:CC:DD:EE:FF'

This probe performs bounded read operations (at most one message/contact entry).
Raw D-Bus responses are kept only in a temporary directory and deleted on exit.
The script never prints names, phone numbers, message subjects, message bodies,
Bluetooth addresses, phone aliases, or OBEX object paths.
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

if [[ ! "$CONNECT_TIMEOUT" =~ ^[1-9][0-9]*$ ]]; then
  echo "NATIVEPAIR_OBEX_TIMEOUT must be a positive integer." >&2
  exit 2
fi

case "$TARGET" in
  map)
    EXPECTED_INTERFACE="org.bluez.obex.MessageAccess1"
    EXPECTED_PROXY_LABEL="MessageAccess"
    ;;
  pbap)
    EXPECTED_INTERFACE="org.bluez.obex.PhonebookAccess1"
    EXPECTED_PROXY_LABEL="PhonebookAccess"
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

echo "nativepair_obex_read_probe_schema=1"
echo "target=$TARGET"
echo "bounded_item_limit=1"
echo "personal_payload_printed=no"

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

printf 'connect %s %s\n' "$DEVICE" "$TARGET" >&"$OBEX_FD"

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

SESSION_PATH="$(
  sed -nE 's/.*Session (\/org\/bluez\/obex\/client\/session[0-9]+).*/\1/p' "$OBEX_LOG" |
    tail -n 1
)"

if [[ -z "$SESSION_PATH" ]]; then
  echo "session_established=no"
  echo "session_error=session_object_missing"
  exit 1
fi

if ! wait_for_log "\[NEW\].*$EXPECTED_PROXY_LABEL|$EXPECTED_PROXY_LABEL /org/bluez/obex/client/session" 2; then
  echo "session_established=no"
  echo "session_error=target_proxy_missing"
  exit 1
fi

if ! busctl --user introspect   org.bluez.obex   "$SESSION_PATH"   "$EXPECTED_INTERFACE" >/dev/null 2>&1; then
  echo "session_established=no"
  echo "session_error=target_interface_missing"
  exit 1
fi

echo "session_established=yes"

array_count() {
  local file="$1"
  awk 'NR == 1 { if ($2 ~ /^[0-9]+$/) print $2; else print "unknown" }' "$file"
}

dbus_error_name() {
  local file="$1"
  grep -Eo 'org\.bluez\.obex\.Error\.[A-Za-z]+' "$file" | head -n 1 || true
}

call_to_file() {
  local output_file="$1"
  shift

  set +e
  busctl --user call "$@" >"$output_file" 2>&1
  local status=$?
  set -e

  return "$status"
}

if [[ "$TARGET" == "map" ]]; then
  FOLDERS_OUT="$TMP_DIR/map-folders.out"
  if call_to_file "$FOLDERS_OUT"     org.bluez.obex "$SESSION_PATH" org.bluez.obex.MessageAccess1     ListFolders 'a{sv}' 1 MaxCount q 16; then
    echo "map_folders_listed=yes"
    count="$(array_count "$FOLDERS_OUT")"
    if [[ "$count" == "unknown" ]]; then
      echo "map_folder_list_nonempty=unknown"
    elif (( count > 0 )); then
      echo "map_folder_list_nonempty=yes"
    else
      echo "map_folder_list_nonempty=no"
    fi
  else
    echo "map_folders_listed=no"
    error_name="$(dbus_error_name "$FOLDERS_OUT")"
    printf 'map_folders_error=%s\n' "${error_name:-unknown}"
    exit 1
  fi

  TELECOM_OUT="$TMP_DIR/map-set-telecom.out"
  if call_to_file "$TELECOM_OUT"     org.bluez.obex "$SESSION_PATH" org.bluez.obex.MessageAccess1     SetFolder s telecom; then
    echo "map_telecom_selected=yes"
  else
    echo "map_telecom_selected=no"
    error_name="$(dbus_error_name "$TELECOM_OUT")"
    printf 'map_telecom_error=%s\n' "${error_name:-unknown}"
    exit 1
  fi

  MSG_OUT="$TMP_DIR/map-set-msg.out"
  if call_to_file "$MSG_OUT"     org.bluez.obex "$SESSION_PATH" org.bluez.obex.MessageAccess1     SetFolder s msg; then
    echo "map_msg_selected=yes"
  else
    echo "map_msg_selected=no"
    error_name="$(dbus_error_name "$MSG_OUT")"
    printf 'map_msg_error=%s\n' "${error_name:-unknown}"
    exit 1
  fi

  MESSAGES_OUT="$TMP_DIR/map-messages.out"
  if call_to_file "$MESSAGES_OUT"     org.bluez.obex "$SESSION_PATH" org.bluez.obex.MessageAccess1     ListMessages 'sa{sv}' inbox 2 MaxCount q 1 Fields as 1 type; then
    echo "map_messages_listed=yes"
    count="$(array_count "$MESSAGES_OUT")"
    if [[ "$count" == "unknown" ]]; then
      echo "map_message_list_nonempty=unknown"
    elif (( count > 0 )); then
      echo "map_message_list_nonempty=yes"
    else
      echo "map_message_list_nonempty=no"
    fi
  else
    echo "map_messages_listed=no"
    error_name="$(dbus_error_name "$MESSAGES_OUT")"
    printf 'map_messages_error=%s\n' "${error_name:-unknown}"
    exit 1
  fi

  echo "read_probe_complete=yes"
  exit 0
fi

SELECT_OUT="$TMP_DIR/pbap-select.out"
if call_to_file "$SELECT_OUT"   org.bluez.obex "$SESSION_PATH" org.bluez.obex.PhonebookAccess1   Select ss int pb; then
  echo "pbap_phonebook_selected=yes"
else
  echo "pbap_phonebook_selected=no"
  error_name="$(dbus_error_name "$SELECT_OUT")"
  printf 'pbap_select_error=%s\n' "${error_name:-unknown}"
  exit 1
fi

SIZE_OUT="$TMP_DIR/pbap-size.out"
if call_to_file "$SIZE_OUT"   org.bluez.obex "$SESSION_PATH" org.bluez.obex.PhonebookAccess1 GetSize; then
  echo "pbap_size_read=yes"
  size="$(awk 'NR == 1 && $1 == "q" && $2 ~ /^[0-9]+$/ { print $2 }' "$SIZE_OUT")"
  if [[ -z "$size" ]]; then
    echo "pbap_phonebook_nonempty=unknown"
  elif (( size > 0 )); then
    echo "pbap_phonebook_nonempty=yes"
  else
    echo "pbap_phonebook_nonempty=no"
  fi
else
  echo "pbap_size_read=no"
  error_name="$(dbus_error_name "$SIZE_OUT")"
  printf 'pbap_size_error=%s\n' "${error_name:-unknown}"
  exit 1
fi

LIST_OUT="$TMP_DIR/pbap-list.out"
if call_to_file "$LIST_OUT"   org.bluez.obex "$SESSION_PATH" org.bluez.obex.PhonebookAccess1   List 'a{sv}' 1 MaxCount q 1; then
  echo "pbap_contacts_listed=yes"
  count="$(array_count "$LIST_OUT")"
  if [[ "$count" == "unknown" ]]; then
    echo "pbap_contact_list_nonempty=unknown"
  elif (( count > 0 )); then
    echo "pbap_contact_list_nonempty=yes"
  else
    echo "pbap_contact_list_nonempty=no"
  fi
else
  echo "pbap_contacts_listed=no"
  error_name="$(dbus_error_name "$LIST_OUT")"
  printf 'pbap_list_error=%s\n' "${error_name:-unknown}"
  exit 1
fi

echo "read_probe_complete=yes"
