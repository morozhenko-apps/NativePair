#!/usr/bin/env bash
set -euo pipefail
trap 'exit 130' INT
trap 'exit 143' TERM
export LC_ALL=C

echo "nativepair_mns_probe_schema=2"

command_present() {
  if command -v "$1" >/dev/null 2>&1; then
    printf 'yes'
  else
    printf 'no'
  fi
}

bool_line() {
  printf '%s=%s\n' "$1" "$2"
}

bool_line bluetoothctl_present "$(command_present bluetoothctl)"
bool_line busctl_present "$(command_present busctl)"
bool_line sdptool_present "$(command_present sdptool)"
bool_line strings_present "$(command_present strings)"
bool_line dpkg_query_present "$(command_present dpkg-query)"

if command -v dpkg-query >/dev/null 2>&1; then
  package_version="$(dpkg-query -W -f='${Version}' bluez-obexd 2>/dev/null || true)"
  printf 'bluez_obexd_package_version=%s\n' "${package_version:-unknown}"
else
  echo "bluez_obexd_package_version=unknown"
fi

if command -v busctl >/dev/null 2>&1 &&
  busctl --user list 2>/dev/null | awk '{print $1}' | grep -Fxq org.bluez.obex; then
  echo "obex_service_available=yes"
else
  echo "obex_service_available=no"
fi

if command -v busctl >/dev/null 2>&1 &&
  busctl --system introspect org.bluez /org/bluez org.bluez.ProfileManager1 >/dev/null 2>&1; then
  echo "profile_manager_available=yes"
else
  echo "profile_manager_available=no"
fi

OBEX_PID="$(
  pgrep -x obexd 2>/dev/null |
    head -n 1 ||
    true
)"

if [[ -n "$OBEX_PID" && -r "/proc/$OBEX_PID/exe" ]]; then
  echo "obexd_process_running=yes"
  OBEX_EXE="$(readlink -f "/proc/$OBEX_PID/exe" 2>/dev/null || true)"
else
  echo "obexd_process_running=no"
  OBEX_EXE=""
fi

MNS_EXPLICITLY_DISABLED=unknown
if [[ -n "$OBEX_PID" && -r "/proc/$OBEX_PID/cmdline" ]]; then
  CMDLINE="$(tr '\0' ' ' < "/proc/$OBEX_PID/cmdline")"
  if grep -Eq -- '(^|[[:space:]])--noplugin(=|[[:space:]]+)([^[:space:],]+,)*mns(,|[[:space:]]|$)' <<<"$CMDLINE"; then
    MNS_EXPLICITLY_DISABLED=yes
  else
    MNS_EXPLICITLY_DISABLED=no
  fi
fi
echo "mns_explicitly_disabled=$MNS_EXPLICITLY_DISABLED"

if [[ -n "$OBEX_EXE" && -r "$OBEX_EXE" ]] && command -v strings >/dev/null 2>&1; then
  STRINGS_OUT="$(mktemp)"
  SDP_OUT=""
  trap 'rm -f "$STRINGS_OUT" "${SDP_OUT:-}"' EXIT
  strings "$OBEX_EXE" >"$STRINGS_OUT"

  if grep -Fq 'x-bt/MAP-NotificationRegistration' "$STRINGS_OUT"; then
    echo "obexd_map_client_signature=yes"
  else
    echo "obexd_map_client_signature=no"
  fi

  if grep -Fq 'x-bt/MAP-event-report' "$STRINGS_OUT"; then
    echo "obexd_mns_event_report_signature=yes"
  else
    echo "obexd_mns_event_report_signature=no"
  fi

  if grep -Fq 'Message Notification server' "$STRINGS_OUT"; then
    echo "obexd_mns_name_signature=yes"
  else
    echo "obexd_mns_name_signature=no"
  fi

  if grep -Fq 'x-bt/MAP-event-report' "$STRINGS_OUT" ||
    grep -Fq 'Message Notification server' "$STRINGS_OUT"; then
    echo "mns_server_compiled=likely_yes"
  else
    echo "mns_server_compiled=likely_no"
  fi
else
  echo "obexd_map_client_signature=unknown"
  echo "obexd_mns_event_report_signature=unknown"
  echo "obexd_mns_name_signature=unknown"
  echo "mns_server_compiled=unknown"
  SDP_OUT=""
  trap 'rm -f "${SDP_OUT:-}"' EXIT
fi

if command -v bluetoothctl >/dev/null 2>&1 &&
  bluetoothctl show 2>/dev/null |
    tr '[:upper:]' '[:lower:]' |
    grep -Fq '00001133-0000-1000-8000-00805f9b34fb'; then
  echo "controller_mns_uuid_visible=yes"
else
  echo "controller_mns_uuid_visible=no"
fi

if command -v sdptool >/dev/null 2>&1; then
  SDP_OUT="$(mktemp)"

  set +e
  sdptool browse local >"$SDP_OUT" 2>&1
  SDP_STATUS=$?
  set -e

  if [[ $SDP_STATUS -eq 0 ]]; then
    echo "local_sdp_query=yes"
    echo "local_sdp_error_class=none"
    if grep -Eqi 'Message Notification|0x1133|00001133-0000-1000-8000-00805f9b34fb' "$SDP_OUT"; then
      echo "local_mns_sdp_record_present=yes"
    else
      echo "local_mns_sdp_record_present=no"
    fi
  else
    echo "local_sdp_query=no"
    if grep -Eqi 'permission|not permitted|access denied' "$SDP_OUT"; then
      echo "local_sdp_error_class=permission"
    elif grep -Eqi 'connection refused|failed to connect|no such file|not available|not found' "$SDP_OUT"; then
      echo "local_sdp_error_class=service_unavailable"
    else
      echo "local_sdp_error_class=unknown"
    fi
    echo "local_mns_sdp_record_present=unknown"
  fi
else
  echo "local_sdp_query=unavailable"
  echo "local_sdp_error_class=tool_missing"
  echo "local_mns_sdp_record_present=unknown"
fi

known_bluez_2315_pattern=no
if [[ -n "${STRINGS_OUT:-}" && "$MNS_EXPLICITLY_DISABLED" == no ]] &&
  grep -Fq 'x-bt/MAP-NotificationRegistration' "$STRINGS_OUT" &&
  grep -Fq 'x-bt/MAP-event-report' "$STRINGS_OUT" &&
  ! bluetoothctl show 2>/dev/null |
    tr '[:upper:]' '[:lower:]' |
    grep -Fq '00001133-0000-1000-8000-00805f9b34fb'; then
  known_bluez_2315_pattern=yes
fi

echo "known_bluez_2315_pattern=$known_bluez_2315_pattern"
echo "note=map_client_and_mns_server_signatures_are_checked_independently"
