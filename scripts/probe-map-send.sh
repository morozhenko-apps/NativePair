#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C

DEVICE="${NATIVEPAIR_DEVICE:-}"
RECIPIENT="${NATIVEPAIR_SMS_RECIPIENT:-}"
CONNECT_TIMEOUT="${NATIVEPAIR_OBEX_TIMEOUT:-45}"
TRANSFER_TIMEOUT="${NATIVEPAIR_SEND_TIMEOUT:-30}"
DO_SEND=no
MESSAGE_TEXT="NativePair MAP send probe"

usage() {
  cat <<'EOF'
Usage:
  ./scripts/probe-map-send.sh
  ./scripts/probe-map-send.sh --send

Environment:
  NATIVEPAIR_DEVICE         Paired phone Bluetooth address.
  NATIVEPAIR_SMS_RECIPIENT  Test SMS recipient in E.164 form, e.g. +351...
  NATIVEPAIR_OBEX_TIMEOUT   MAP connect timeout in seconds (default 45).
  NATIVEPAIR_SEND_TIMEOUT   PushMessage transfer timeout in seconds (default 30).

Default mode is a no-side-effect preflight. It creates a MAP session, verifies
SMS_GSM support, prepares a temporary bMessage, and exits without PushMessage.

--send performs one real outgoing SMS attempt through MAP. The recipient and
message payload are never printed. Retry is disabled to reduce duplicate-send
risk. Temporary payload and D-Bus logs are deleted on exit.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --send)
      DO_SEND=yes
      shift
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
  echo "Invalid or missing Bluetooth address. Set NATIVEPAIR_DEVICE first." >&2
  exit 2
fi

if [[ ! "$RECIPIENT" =~ ^\+[1-9][0-9]{6,14}$ ]]; then
  echo "Invalid or missing test recipient. Set NATIVEPAIR_SMS_RECIPIENT in E.164 form." >&2
  exit 2
fi

for value_name in CONNECT_TIMEOUT TRANSFER_TIMEOUT; do
  value="${!value_name}"
  if [[ ! "$value" =~ ^[1-9][0-9]{0,17}$ ]] || (( value > 922337203685477580 )); then
    echo "$value_name must be a positive integer." >&2
    exit 2
  fi
done

for command in busctl bluetoothctl obexctl stdbuf mktemp wc tail grep sed od tr python3; do
  if ! command -v "$command" >/dev/null 2>&1; then
    echo "Required command is missing: $command" >&2
    exit 1
  fi
done

echo "nativepair_map_send_probe_schema=2"
echo "personal_payload_printed=no"
echo "send_requested=$DO_SEND"

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
MONITOR_LOG="$TMP_DIR/busctl-monitor.log"
PUSH_REPLY="$TMP_DIR/push.reply"
BMSG_FILE="$TMP_DIR/nativepair-send.bmsg"
OBEX_INPUT="$TMP_DIR/obexctl.in"

OBEX_PID=""
OBEX_FD=""
MONITOR_PID=""
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

  if [[ -n "$MONITOR_PID" ]] && kill -0 "$MONITOR_PID" 2>/dev/null; then
    kill "$MONITOR_PID" 2>/dev/null || true
    wait "$MONITOR_PID" 2>/dev/null || true
  fi

  rm -rf "$TMP_DIR"
  exit "$status"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
mkfifo "$OBEX_INPUT"

stdbuf -oL -eL busctl --user monitor org.bluez.obex >"$MONITOR_LOG" 2>&1 &
MONITOR_PID=$!
MONITOR_READY=no
for _ in {1..50}; do
  if grep -Fq 'Monitoring bus message stream' "$MONITOR_LOG"; then
    MONITOR_READY=yes
    break
  fi
  kill -0 "$MONITOR_PID" 2>/dev/null || break
  sleep 0.1
done

if [[ "$MONITOR_READY" != yes ]] || ! kill -0 "$MONITOR_PID" 2>/dev/null; then
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
    if [[ "$file" == "$OBEX_LOG" ]] && ! kill -0 "$OBEX_PID" 2>/dev/null; then
      return 1
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

SUPPORTED_TYPES="$TMP_DIR/supported-types"
if busctl --user get-property org.bluez.obex "$SESSION_PATH"   org.bluez.obex.MessageAccess1 SupportedTypes >"$SUPPORTED_TYPES" 2>/dev/null &&
  grep -Fq '"SMS_GSM"' "$SUPPORTED_TYPES"; then
  echo "sms_gsm_supported=yes"
else
  echo "sms_gsm_supported=no"
  exit 1
fi

if ! busctl --user call org.bluez.obex "$SESSION_PATH"   org.bluez.obex.MessageAccess1 SetFolder s telecom >/dev/null 2>&1; then
  echo "map_telecom_selected=no"
  exit 1
fi
echo "map_telecom_selected=yes"

if ! busctl --user call org.bluez.obex "$SESSION_PATH"   org.bluez.obex.MessageAccess1 SetFolder s msg >/dev/null 2>&1; then
  echo "map_msg_selected=no"
  exit 1
fi
echo "map_msg_selected=yes"

MESSAGE_BYTES="$(printf '%s' "$MESSAGE_TEXT" | wc -c)"
# Android's MAP bMessage builder defines LENGTH as:
# BEGIN:MSG + CRLF + message + CRLF + END:MSG + CRLF.
MSG_LENGTH="$((MESSAGE_BYTES + 22))"

{
  printf 'BEGIN:BMSG\r\n'
  printf 'VERSION:1.0\r\n'
  printf 'STATUS:UNREAD\r\n'
  printf 'TYPE:SMS_GSM\r\n'
  printf 'FOLDER:telecom/msg/outbox\r\n'
  printf 'BEGIN:BENV\r\n'
  printf 'BEGIN:VCARD\r\n'
  printf 'VERSION:2.1\r\n'
  printf 'N:;;;;\r\n'
  printf 'TEL:%s\r\n' "$RECIPIENT"
  printf 'END:VCARD\r\n'
  printf 'BEGIN:BBODY\r\n'
  printf 'CHARSET:UTF-8\r\n'
  printf 'LENGTH:%s\r\n' "$MSG_LENGTH"
  printf 'BEGIN:MSG\r\n'
  printf '%s\r\n' "$MESSAGE_TEXT"
  printf 'END:MSG\r\n'
  printf 'END:BBODY\r\n'
  printf 'END:BENV\r\n'
  printf 'END:BMSG\r\n'
} >"$BMSG_FILE"
chmod 600 "$BMSG_FILE"

# Reject malformed CRLF framing before any PushMessage side effect.
if ! grep -Fqx $'BEGIN:MSG\r' "$BMSG_FILE" ||
  ! grep -Fqx $'END:MSG\r' "$BMSG_FILE" ||
  ! grep -Fqx $'END:BBODY\r' "$BMSG_FILE" ||
  [[ "$(tail -c 2 "$BMSG_FILE" | od -An -t x1 | tr -d '[:space:]')" != "0d0a" ]]; then
  echo "bmessage_prepared=no"
  echo "bmessage_structure_valid=no"
  exit 1
fi

echo "bmessage_prepared=yes"
echo "bmessage_structure_valid=yes"
echo "bmessage_type=SMS_GSM"
echo "retry_enabled=no"
echo "transparent_enabled=yes"

if [[ "$DO_SEND" != yes ]]; then
  echo "actual_send=no"
  echo "send_probe_complete=preflight"
  echo "note=rerun_with_--send_only_after_confirming_the_hidden_recipient"
  exit 0
fi

echo "actual_send=yes"

MONITOR_BASELINE="$(wc -l <"$MONITOR_LOG")"

set +e
busctl --user call org.bluez.obex "$SESSION_PATH"   org.bluez.obex.MessageAccess1 PushMessage 'ssa{sv}'   "$BMSG_FILE" outbox 3   Transparent b true   Retry b false   Charset s utf8 >"$PUSH_REPLY" 2>&1
PUSH_STATUS=$?
set -e

if [[ $PUSH_STATUS -ne 0 ]]; then
  echo "push_message_accepted=no"
  echo "send_probe_complete=no"
  echo "send_error=push_message_call_failed"
  exit 1
fi
echo "push_message_accepted=yes"

TRANSFER_PATH="$(
  sed -nE 's/^oa\{sv\} "([^"]+)".*/\1/p' "$PUSH_REPLY" |
    head -n 1
)"

if [[ -n "$TRANSFER_PATH" ]]; then
  echo "transfer_path_returned=yes"
else
  echo "transfer_path_returned=no"
fi

transfer_result=unknown
elapsed=0
while (( elapsed < TRANSFER_TIMEOUT * 10 )); do
  NEW_LOG="$TMP_DIR/monitor-new.log"
  tail -n "+$((MONITOR_BASELINE + 1))" "$MONITOR_LOG" >"$NEW_LOG" 2>/dev/null || true

  transfer_result="$(python3 "$(dirname -- "${BASH_SOURCE[0]}")/probe_obex_monitor.py" "$NEW_LOG" "$TRANSFER_PATH")"
  if [[ "$transfer_result" == complete || "$transfer_result" == error ]]; then
    break
  fi

  if ! kill -0 "$OBEX_PID" 2>/dev/null; then
    transfer_result=session_lost
    break
  fi

  sleep 0.1
  ((elapsed += 1))
done

echo "push_transfer_status=$transfer_result"

case "$transfer_result" in
  complete)
    echo "send_probe_complete=yes"
    echo "note=map_push_transfer_completed_verify_recipient_received_exactly_one_sms"
    ;;
  error)
    echo "send_probe_complete=no"
    echo "send_error=transfer_error"
    exit 1
    ;;
  session_lost)
    echo "send_probe_complete=no"
    echo "send_error=session_lost"
    exit 1
    ;;
  *)
    echo "send_probe_complete=inconclusive"
    echo "note=push_was_accepted_but_transfer_completion_was_not_observed"
    ;;
esac
