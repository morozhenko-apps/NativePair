#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C

echo "nativepair_mns_probe_schema=1"

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

if [[ -n "$OBEX_PID" && -r "/proc/$OBEX_PID/cmdline" ]]; then
  CMDLINE="$(tr '\0' ' ' < "/proc/$OBEX_PID/cmdline")"
  if grep -Eq -- '--noplugin([=[:space:]][^ ]*,?)*mns|--noplugin[=[:space:]]+mns' <<<"$CMDLINE"; then
    echo "mns_explicitly_disabled=yes"
  else
    echo "mns_explicitly_disabled=no"
  fi
else
  echo "mns_explicitly_disabled=unknown"
fi

if [[ -n "$OBEX_EXE" && -r "$OBEX_EXE" ]] && command -v strings >/dev/null 2>&1; then
  if strings "$OBEX_EXE" | grep -Fq 'Message Notification server'; then
    echo "mns_plugin_compiled=yes"
  else
    echo "mns_plugin_compiled=no"
  fi
else
  echo "mns_plugin_compiled=unknown"
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
  trap 'rm -f "$SDP_OUT"' EXIT

  set +e
  sdptool browse local >"$SDP_OUT" 2>&1
  SDP_STATUS=$?
  set -e

  if [[ $SDP_STATUS -eq 0 ]]; then
    echo "local_sdp_query=yes"
    if grep -Eqi 'Message Notification|0x1133|00001133-0000-1000-8000-00805f9b34fb' "$SDP_OUT"; then
      echo "local_mns_sdp_record_present=yes"
    else
      echo "local_mns_sdp_record_present=no"
    fi
  else
    echo "local_sdp_query=no"
    echo "local_mns_sdp_record_present=unknown"
  fi
else
  echo "local_sdp_query=unavailable"
  echo "local_mns_sdp_record_present=unknown"
fi

echo "note=mns_profile_presence_is_prerequisite_for_remote_map_event_delivery"
