#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C

DEVICE="${NATIVEPAIR_DEVICE:-}"
HOST_ONLY=no

usage() {
  cat <<'EOF'
Usage:
  ./scripts/probe-bluetooth.sh
  ./scripts/probe-bluetooth.sh --device AA:BB:CC:DD:EE:FF
  ./scripts/probe-bluetooth.sh --host-only

You may set NATIVEPAIR_DEVICE once in the current shell instead of passing
--device repeatedly:

  export NATIVEPAIR_DEVICE='AA:BB:CC:DD:EE:FF'

The output is intentionally privacy-safe: it does not print phone names,
Bluetooth addresses, message contents, contacts, or notification contents.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --device)
      if [[ $# -lt 2 ]]; then
        echo "--device requires a Bluetooth address." >&2
        exit 2
      fi
      DEVICE="$2"
      shift 2
      ;;
    --host-only)
      HOST_ONLY=yes
      DEVICE=""
      shift
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

if [[ -n "$DEVICE" ]] && [[ ! "$DEVICE" =~ ^([[:xdigit:]]{2}:){5}[[:xdigit:]]{2}$ ]]; then
  echo "Invalid Bluetooth address format." >&2
  exit 2
fi

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

echo "nativepair_probe_schema=2"
echo "probe_scope=host$([[ -n "$DEVICE" ]] && printf '+device')"

bool_line bluetoothctl_present "$(command_present bluetoothctl)"
bool_line busctl_present "$(command_present busctl)"
bool_line obexctl_present "$(command_present obexctl)"

if command -v bluetoothctl >/dev/null 2>&1; then
  version="$(bluetoothctl --version 2>/dev/null | head -n 1 | tr -cd '[:alnum:].:_ -')"
  printf 'bluez_version=%s\n' "${version:-unknown}"

  adapter_count="$(
    bluetoothctl list 2>/dev/null |
      awk '/^Controller / { count += 1 } END { print count + 0 }'
  )"
  printf 'adapter_count=%s\n' "$adapter_count"

  paired_count="$(
    {
      bluetoothctl devices Paired 2>/dev/null ||
        bluetoothctl paired-devices 2>/dev/null ||
        true
    } |
      awk '/^Device / { count += 1 } END { print count + 0 }'
  )"
  printf 'paired_device_count=%s\n' "$paired_count"
else
  echo "bluez_version=unavailable"
  echo "adapter_count=0"
  echo "paired_device_count=0"
fi

if command -v systemctl >/dev/null 2>&1 &&
  systemctl is-active --quiet bluetooth.service 2>/dev/null; then
  bool_line bluetooth_service_active yes
else
  bool_line bluetooth_service_active no
fi

if command -v busctl >/dev/null 2>&1 &&
  busctl --user list >/dev/null 2>&1; then
  bool_line session_dbus_available yes
else
  bool_line session_dbus_available no
fi

if command -v systemctl >/dev/null 2>&1 &&
  systemctl --user is-active --quiet mpris-proxy.service 2>/dev/null; then
  bool_line mpris_proxy_user_service_active yes
else
  bool_line mpris_proxy_user_service_active no
fi

if [[ "$HOST_ONLY" == yes || -z "$DEVICE" ]]; then
  exit 0
fi

if ! command -v bluetoothctl >/dev/null 2>&1; then
  echo "Cannot probe a device without bluetoothctl." >&2
  exit 1
fi

info="$(bluetoothctl info "$DEVICE" 2>/dev/null || true)"
if [[ -z "$info" ]]; then
  bool_line device_visible no
  exit 1
fi

bool_line device_visible yes

property_is_yes() {
  local property="$1"
  if grep -Eq "^[[:space:]]*$property:[[:space:]]+yes$" <<<"$info"; then
    printf 'yes'
  else
    printf 'no'
  fi
}

bool_line device_paired "$(property_is_yes Paired)"
bool_line device_trusted "$(property_is_yes Trusted)"
bool_line device_connected "$(property_is_yes Connected)"

lower_info="$(tr '[:upper:]' '[:lower:]' <<<"$info")"

uuid_present() {
  local uuid="$1"
  if grep -Fq "$uuid" <<<"$lower_info"; then
    printf 'yes'
  else
    printf 'no'
  fi
}

bool_line advertised_map_mse "$(uuid_present 00001132-0000-1000-8000-00805f9b34fb)"
bool_line advertised_pbap_pse "$(uuid_present 0000112f-0000-1000-8000-00805f9b34fb)"
bool_line advertised_hfp_ag "$(uuid_present 0000111f-0000-1000-8000-00805f9b34fb)"
bool_line advertised_ancs "$(uuid_present 7905f431-b5ce-4e99-a40f-4b1e122d00d0)"

echo "note=advertisement_is_not_end_to_end_support"
