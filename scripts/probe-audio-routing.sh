#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C

DEVICE="${NATIVEPAIR_DEVICE:-}"
TELEPHONY_SERVICE="org.pipewire.Telephony"
TELEPHONY_MANAGER="/org/pipewire/Telephony"
TRANSPORT_IFACE="org.pipewire.Telephony.AudioGatewayTransport1"

if [[ ! "$DEVICE" =~ ^([[:xdigit:]]{2}:){5}[[:xdigit:]]{2}$ ]]; then
  echo "Invalid or missing Bluetooth address. Set NATIVEPAIR_DEVICE first." >&2
  exit 2
fi

for command in awk busctl grep head mktemp python3 pw-dump sed wpctl; do
  if ! command -v "$command" >/dev/null 2>&1; then
    echo "Required command is missing: $command" >&2
    exit 1
  fi
done

TMP_DIR="$(mktemp -d)"
MODEMS_REPLY="$TMP_DIR/modems.reply"
STATE_REPLY="$TMP_DIR/state.reply"
PW_DUMP="$TMP_DIR/pw-dump.json"
ROUTING_RESULT="$TMP_DIR/routing.result"
DEFAULT_SINK_REPLY="$TMP_DIR/default-sink.reply"
DEFAULT_SOURCE_REPLY="$TMP_DIR/default-source.reply"

cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

echo "nativepair_audio_routing_probe_schema=1"
echo "personal_payload_printed=no"
echo "routing_changed=no"

AG_PATH=""
if busctl --user call "$TELEPHONY_SERVICE" "$TELEPHONY_MANAGER"   org.ofono.Manager GetModems >"$MODEMS_REPLY" 2>/dev/null; then
  AG_PATH="$(awk -F'"' '
      { for (i = 2; i <= NF; i += 2) if ($i ~ /^\/org\/pipewire\/Telephony\/ag[0-9]+$/) seen[$i] = 1 }
      END { for (path in seen) { count++; last = path } if (count == 1) print last }
    ' "$MODEMS_REPLY")"
fi

if [[ -n "$AG_PATH" ]]; then
  echo "telephony_audio_gateway_present=yes"
  if busctl --user get-property "$TELEPHONY_SERVICE" "$AG_PATH"     "$TRANSPORT_IFACE" State >"$STATE_REPLY" 2>/dev/null; then
    STATE="$(sed -nE 's/^s "(idle|pending|active|error)"$/\1/p' "$STATE_REPLY")"
    printf 'transport_state=%s\n' "${STATE:-unknown}"
  else
    echo "transport_state=unknown"
  fi
else
  echo "telephony_audio_gateway_present=no"
  echo "transport_state=unavailable"
fi

if ! pw-dump >"$PW_DUMP" 2>/dev/null; then
  echo "pipewire_snapshot_available=no"
  exit 1
fi
echo "pipewire_snapshot_available=yes"

DEFAULT_SINK_ID=""
DEFAULT_SOURCE_ID=""

if wpctl inspect @DEFAULT_AUDIO_SINK@ >"$DEFAULT_SINK_REPLY" 2>/dev/null; then
  DEFAULT_SINK_ID="$(sed -nE 's/^id ([0-9]+),.*/\1/p' "$DEFAULT_SINK_REPLY" | head -n 1)"
fi

if wpctl inspect @DEFAULT_AUDIO_SOURCE@ >"$DEFAULT_SOURCE_REPLY" 2>/dev/null; then
  DEFAULT_SOURCE_ID="$(sed -nE 's/^id ([0-9]+),.*/\1/p' "$DEFAULT_SOURCE_REPLY" | head -n 1)"
fi

python3 - "$PW_DUMP" "$DEVICE" "$DEFAULT_SINK_ID" "$DEFAULT_SOURCE_ID" "$(dirname -- "${BASH_SOURCE[0]}")" >"$ROUTING_RESULT" <<'PY' || { cat "$ROUTING_RESULT"; exit 1; }
import json
import sys
sys.path.insert(0, sys.argv[-1])
from probe_audio_graph import hfp_direction, is_hfp, load_nodes

path, device, default_sink_id, default_source_id = sys.argv[1:5]
try:
    data = load_nodes(path)
except (OSError, ValueError):
    print("pipewire_snapshot_valid=no")
    sys.exit(1)

hfp_nodes = []
for obj in data:
    info = obj.get("info") or {}
    props = info.get("props") or {}
    if props.get("api.bluez5.address") != device:
        continue
    if not is_hfp(props):
        continue
    hfp_nodes.append((str(obj.get("id")), props))

source_ids = {node_id for node_id, props in hfp_nodes if props.get("media.class") == "Audio/Source"}
sink_ids = {node_id for node_id, props in hfp_nodes if props.get("media.class") == "Audio/Sink"}
source_present = any(hfp_direction(props) == "source" for _, props in hfp_nodes)
sink_present = any(hfp_direction(props) == "sink" for _, props in hfp_nodes)

print(f"hfp_node_count={len(hfp_nodes)}")
print(f"hfp_source_node_present={'yes' if source_present else 'no'}")
print(f"hfp_sink_node_present={'yes' if sink_present else 'no'}")
print(f"default_sink_snapshot_available={'yes' if default_sink_id else 'no'}")
print(f"default_source_snapshot_available={'yes' if default_source_id else 'no'}")
print(f"default_sink_is_phone_hfp={'yes' if default_sink_id in sink_ids else 'no'}")
print(f"default_source_is_phone_hfp={'yes' if default_source_id in source_ids else 'no'}")
print(f"orphan_hfp_nodes_present={'yes' if hfp_nodes else 'no'}")
PY

cat "$ROUTING_RESULT"
echo "probe_complete=yes"
echo "note=read_only_snapshot_no_default_device_or_link_was_changed"
