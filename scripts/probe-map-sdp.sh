#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C

DEVICE="${NATIVEPAIR_DEVICE:-}"

usage() {
  cat <<'EOF'
Usage:
  ./scripts/probe-map-sdp.sh

Set the phone once in the current shell:

  export NATIVEPAIR_DEVICE='AA:BB:CC:DD:EE:FF'

The probe queries only the remote MAP MAS SDP record and reports whether the
attributes required by BlueZ are present. Raw SDP output is stored only in a
temporary file and deleted on exit. The Bluetooth address and service payload
are never printed.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
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

for command in sdptool timeout mktemp; do
  if ! command -v "$command" >/dev/null 2>&1; then
    echo "Required command is missing: $command" >&2
    exit 1
  fi
done

echo "nativepair_map_sdp_probe_schema=1"
echo "personal_payload_printed=no"

SDP_OUT="$(mktemp)"
trap 'rm -f "$SDP_OUT"' EXIT

set +e
timeout 20s sdptool search --bdaddr "$DEVICE" --xml 0x1132 >"$SDP_OUT" 2>&1
SDP_STATUS=$?
set -e

if [[ $SDP_STATUS -eq 124 ]]; then
  echo "remote_sdp_query=no"
  echo "remote_sdp_error=timeout"
  exit 1
elif [[ $SDP_STATUS -ne 0 ]]; then
  echo "remote_sdp_query=no"
  echo "remote_sdp_error=query_failed"
  exit 1
fi

echo "remote_sdp_query=yes"

if grep -Eqi '<attribute[^>]+id="0x0315"|<attribute[^>]+id="0x315"' "$SDP_OUT"; then
  echo "mas_instance_id_present=yes"
else
  echo "mas_instance_id_present=no"
fi

if grep -Eqi '<attribute[^>]+id="0x0316"|<attribute[^>]+id="0x316"' "$SDP_OUT"; then
  echo "supported_message_types_present=yes"
else
  echo "supported_message_types_present=no"
fi

if grep -Eqi '<attribute[^>]+id="0x0317"|<attribute[^>]+id="0x317"' "$SDP_OUT"; then
  echo "map_supported_features_present=yes"
else
  echo "map_supported_features_present=no"
fi

if grep -Eqi 'uuid[^>]+value="0x1132"|uuid[^>]+value="00001132' "$SDP_OUT"; then
  echo "map_mas_record_confirmed=yes"
else
  echo "map_mas_record_confirmed=unknown"
fi

echo "note=bluez_requires_mas_instance_id_before_it_queues_map_notification_registration"
