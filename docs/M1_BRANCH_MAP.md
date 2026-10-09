# M1 source branch map

Status: planned, 2026-10-09. All existing source branches below require both outcomes or each case arm in the named contract family. Loop zero/one/exhaustion, short-circuit guards and cleanup exits are included. This source index is supplementary to the semantic inventory in M1_AUTOMATED_VERIFICATION.md; line numbers describe the planning baseline, not measured coverage.

## scripts/build-deb.sh

| Source line | Decision / method | Planned assertion family |
| --- | --- | --- |
| 4 | ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)" | BUILD-DEB: success, rejection, unavailable/malformed and cleanup as applicable |
| 7 | for command in cargo dpkg dpkg-deb python3 sha256sum; do | BUILD-DEB: success, rejection, unavailable/malformed and cleanup as applicable |
| 8 | if ! command -v "$command" >/dev/null 2>&1; then | BUILD-DEB: success, rejection, unavailable/malformed and cleanup as applicable |
| 15 | if [[ -z "$VERSION" ]]; then | BUILD-DEB: success, rejection, unavailable/malformed and cleanup as applicable |
| 22 | if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+([.-][0-9A-Za-z.-]+)?$ ]]; then | BUILD-DEB: success, rejection, unavailable/malformed and cleanup as applicable |
| 28 | case "$ARCH" in | BUILD-DEB: success, rejection, unavailable/malformed and cleanup as applicable |
| 29 | amd64&#124;arm64) | BUILD-DEB: success, rejection, unavailable/malformed and cleanup as applicable |
| 31 | *) | BUILD-DEB: success, rejection, unavailable/malformed and cleanup as applicable |
| 60 | if [[ -z "${SOURCE_DATE_EPOCH:-}" ]] && command -v git >/dev/null 2>&1; then | BUILD-DEB: success, rejection, unavailable/malformed and cleanup as applicable |
| 61 | SOURCE_DATE_EPOCH="$(git log -1 --format=%ct 2>/dev/null &#124;&#124; true)" | BUILD-DEB: success, rejection, unavailable/malformed and cleanup as applicable |
| 63 | if [[ -n "${SOURCE_DATE_EPOCH:-}" ]]; then | BUILD-DEB: success, rejection, unavailable/malformed and cleanup as applicable |
| 65 | while IFS= read -r -d '' path; do | BUILD-DEB: success, rejection, unavailable/malformed and cleanup as applicable |
| 67 | done < <(find "$PACKAGE_ROOT" -print0) | BUILD-DEB: success, rejection, unavailable/malformed and cleanup as applicable |

## scripts/probe-audio-health.sh

| Source line | Decision / method | Planned assertion family |
| --- | --- | --- |
| 8 | if [[ ! "$ITERATIONS" =~ ^[0-9]+$ ]] &#124;&#124; (( ITERATIONS < 2 &#124;&#124; ITERATIONS > 60 )); then | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 13 | for command in grep journalctl mktemp pw-dump python3 pw-top sed systemctl timeout wpctl; do | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 14 | if ! command -v "$command" >/dev/null 2>&1; then | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 29 | cleanup() { | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 39 | if systemctl --user is-active --quiet pipewire.service 2>/dev/null; then | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 45 | if systemctl --user is-active --quiet wireplumber.service 2>/dev/null; then | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 51 | if ! pw-dump >"$PW_DUMP" 2>/dev/null; then | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 60 | if wpctl inspect @DEFAULT_AUDIO_SINK@ >"$DEFAULT_SINK_REPLY" 2>/dev/null; then | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 64 | if wpctl inspect @DEFAULT_AUDIO_SOURCE@ >"$DEFAULT_SOURCE_REPLY" 2>/dev/null; then | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 73 | if [[ $PW_TOP_STATUS -ne 0 ]]; then | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 90 | seen_ids = set() | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 95 | nonzero_pairs = set() | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 98 | for raw in handle: | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 99 | line = raw.strip() | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 100 | if not line: | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 102 | if line.startswith("S   ID  QUANT"): | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 106 | parts = line.split() | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 107 | if len(parts) < 9: | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 116 | if state not in {"E", "C", "S", "I", "R", "t", "T", "!"}: | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 118 | if not node_id.isdigit() or not err.isdigit(): | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 122 | if state in {"R", "t", "T"}: | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 124 | if state == "E": | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 127 | nid = int(node_id) | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 128 | value = int(err) | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 129 | seen_ids.add(nid) | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 130 | states_seen.setdefault(nid, set()).add(state) | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 131 | first_err.setdefault(nid, value) | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 133 | max_err[nid] = max(max_err.get(nid, value), value) | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 135 | if quant.isdigit() and rate.isdigit(): | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 136 | q = int(quant) | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 137 | r = int(rate) | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 138 | if q > 0 and r > 0: | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 139 | nonzero_pairs.add((q, r)) | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 142 | nid: max_err.get(nid, 0) - first_err.get(nid, 0) | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 143 | for nid in seen_ids | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 144 | if max_err.get(nid, 0) - first_err.get(nid, 0) > 0 | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 148 | dump = json.load(handle) | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 151 | for obj in dump: | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 152 | if obj.get("type") != "PipeWire:Interface:Node": | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 154 | obj_id = obj.get("id") | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 155 | if obj_id is None: | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 160 | def props_for(nid): | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 161 | return props_by_id.get(str(nid), {}) | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 163 | def is_bluetooth(props): | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 165 | bool(props.get("api.bluez5.address")) | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 167 | or bool(props.get("api.bluez5.profile")) | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 170 | def is_hfp(props): | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 173 | def media_class(props): | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 174 | return str(props.get("media.class") or "") | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 176 | def default_kind(node_id): | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 177 | if not node_id: | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 179 | props = props_by_id.get(node_id) | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 180 | if props is None: | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 186 | for nid, delta in growth.items() | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 187 | if states_seen.get(nid, set()) & {"R", "t", "T"} | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 190 | nid: delta for nid, delta in growth.items() if is_bluetooth(props_for(nid)) | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 193 | nid: delta for nid, delta in growth.items() if is_hfp(props_for(nid)) | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 197 | for nid, delta in growth.items() | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 198 | if media_class(props_for(nid)).startswith("Stream/Output/Audio") | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 202 | for nid, delta in growth.items() | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 203 | if media_class(props_for(nid)) == "Audio/Sink" | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 207 | for nid, delta in growth.items() | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 208 | if media_class(props_for(nid)) == "Audio/Source" | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 211 | set(bluetooth_growth) | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 212 | &#124; set(output_stream_growth) | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 213 | &#124; set(audio_sink_growth) | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 214 | &#124; set(audio_source_growth) | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 221 | positive_now = sum(1 for value in last_err.values() if value > 0) | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 222 | max_delta = max(growth.values(), default=0) | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 223 | max_value = max(last_err.values(), default=0) | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 225 | print(f"pw_top_snapshots={snapshots}") | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 226 | print(f"pw_top_rows_parsed={rows}") | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 227 | print(f"running_rows_observed={running_rows}") | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 228 | print(f"error_state_rows_observed={error_state_rows}") | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 229 | print(f"nodes_with_nonzero_err_at_end={positive_now}") | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 230 | print(f"nodes_with_err_growth={len(growth)}") | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 231 | print(f"nodes_with_err_growth_while_running={len(running_growth)}") | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 232 | print(f"max_single_node_err_delta={max_delta}") | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 233 | print(f"max_err_value_at_end={max_value}") | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 234 | print(f"xrun_or_error_growth_observed={'yes' if growth else 'no'}") | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 235 | print(f"nonzero_quantum_rate_pair_count={len(nonzero_pairs)}") | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 237 | print(f"default_sink_snapshot_available={'yes' if default_sink_id else 'no'}") | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 238 | print(f"default_source_snapshot_available={'yes' if default_source_id else 'no'}") | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 239 | print(f"default_sink_is_bluetooth={default_kind(default_sink_id)}") | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 240 | print(f"default_source_is_bluetooth={default_kind(default_source_id)}") | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 241 | print(f"default_sink_err_growth={'yes' if default_sink_delta > 0 else 'no'}") | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 242 | print(f"default_sink_err_delta={default_sink_delta}") | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 243 | print(f"default_source_err_growth={'yes' if default_source_delta > 0 else 'no'}") | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 244 | print(f"default_source_err_delta={default_source_delta}") | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 246 | print(f"bluetooth_nodes_with_err_growth={len(bluetooth_growth)}") | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 247 | print(f"hfp_nodes_with_err_growth={len(hfp_growth)}") | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 248 | print(f"output_stream_nodes_with_err_growth={len(output_stream_growth)}") | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 249 | print(f"audio_sink_nodes_with_err_growth={len(audio_sink_growth)}") | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 250 | print(f"audio_source_nodes_with_err_growth={len(audio_source_growth)}") | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 251 | print(f"unclassified_nodes_with_err_growth={len(unclassified_growth)}") | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 252 | print(f"bluetooth_err_growth_observed={'yes' if bluetooth_growth else 'no'}") | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 253 | print(f"hfp_err_growth_observed={'yes' if hfp_growth else 'no'}") | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 254 | print(f"output_stream_err_growth_observed={'yes' if output_stream_growth else 'no'}") | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 259 | journalctl --user -u pipewire.service --since "-$RECENT_WINDOW" -p warning   --no-pager --output=cat >"$PIPEWIRE_LOG" 2>/dev/null &#124;&#124; true | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 260 | journalctl --user -u wireplumber.service --since "-$RECENT_WINDOW" -p warning   --no-pager --output=cat >"$WIREPLUMBER_LOG" 2>/dev/null &#124;&#124; true | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 262 | PIPEWIRE_WARNINGS="$(grep -cve '^[[:space:]]*$' "$PIPEWIRE_LOG" &#124;&#124; true)" | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 263 | WIREPLUMBER_WARNINGS="$(grep -cve '^[[:space:]]*$' "$WIREPLUMBER_LOG" &#124;&#124; true)" | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 268 | if grep -Eqi 'xrun&#124;underrun&#124;overrun&#124;deadline&#124;missed' "$PIPEWIRE_LOG" "$WIREPLUMBER_LOG"; then | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 274 | if grep -Eqi 'bluez&#124;bluetooth&#124;sco&#124;hfp&#124;transport' "$PIPEWIRE_LOG" "$WIREPLUMBER_LOG"; then | AUDIO-HEALTH: success, rejection, unavailable/malformed and cleanup as applicable |

## scripts/probe-audio-routing.sh

| Source line | Decision / method | Planned assertion family |
| --- | --- | --- |
| 10 | if [[ ! "$DEVICE" =~ ^([[:xdigit:]]{2}:){5}[[:xdigit:]]{2}$ ]]; then | AUDIO-ROUTING: success, rejection, unavailable/malformed and cleanup as applicable |
| 15 | for command in busctl grep head mktemp python3 pw-dump sed wpctl; do | AUDIO-ROUTING: success, rejection, unavailable/malformed and cleanup as applicable |
| 16 | if ! command -v "$command" >/dev/null 2>&1; then | AUDIO-ROUTING: success, rejection, unavailable/malformed and cleanup as applicable |
| 30 | cleanup() { | AUDIO-ROUTING: success, rejection, unavailable/malformed and cleanup as applicable |
| 40 | if busctl --user call "$TELEPHONY_SERVICE" "$TELEPHONY_MANAGER"   org.ofono.Manager GetModems >"$MODEMS_REPLY" 2>/dev/null; then | AUDIO-ROUTING: success, rejection, unavailable/malformed and cleanup as applicable |
| 43 | grep -oE '/org/pipewire/Telephony/ag[0-9]+' "$MODEMS_REPLY" &#124;&#124; true | AUDIO-ROUTING: success, rejection, unavailable/malformed and cleanup as applicable |
| 49 | if [[ -n "$AG_PATH" ]]; then | AUDIO-ROUTING: success, rejection, unavailable/malformed and cleanup as applicable |
| 51 | if busctl --user get-property "$TELEPHONY_SERVICE" "$AG_PATH"     "$TRANSPORT_IFACE" State >"$STATE_REPLY" 2>/dev/null; then | AUDIO-ROUTING: success, rejection, unavailable/malformed and cleanup as applicable |
| 62 | if ! pw-dump >"$PW_DUMP" 2>/dev/null; then | AUDIO-ROUTING: success, rejection, unavailable/malformed and cleanup as applicable |
| 71 | if wpctl inspect @DEFAULT_AUDIO_SINK@ >"$DEFAULT_SINK_REPLY" 2>/dev/null; then | AUDIO-ROUTING: success, rejection, unavailable/malformed and cleanup as applicable |
| 75 | if wpctl inspect @DEFAULT_AUDIO_SOURCE@ >"$DEFAULT_SOURCE_REPLY" 2>/dev/null; then | AUDIO-ROUTING: success, rejection, unavailable/malformed and cleanup as applicable |
| 85 | data = json.load(handle) | AUDIO-ROUTING: success, rejection, unavailable/malformed and cleanup as applicable |
| 88 | for obj in data: | AUDIO-ROUTING: success, rejection, unavailable/malformed and cleanup as applicable |
| 89 | if obj.get("type") != "PipeWire:Interface:Node": | AUDIO-ROUTING: success, rejection, unavailable/malformed and cleanup as applicable |
| 93 | if props.get("api.bluez5.address") != device: | AUDIO-ROUTING: success, rejection, unavailable/malformed and cleanup as applicable |
| 95 | if props.get("api.bluez5.profile") != "headset-head-unit": | AUDIO-ROUTING: success, rejection, unavailable/malformed and cleanup as applicable |
| 97 | hfp_nodes.append((str(obj.get("id")), props.get("media.class"))) | AUDIO-ROUTING: success, rejection, unavailable/malformed and cleanup as applicable |
| 102 | print(f"hfp_node_count={len(hfp_nodes)}") | AUDIO-ROUTING: success, rejection, unavailable/malformed and cleanup as applicable |
| 103 | print(f"hfp_source_node_present={'yes' if source_ids else 'no'}") | AUDIO-ROUTING: success, rejection, unavailable/malformed and cleanup as applicable |
| 104 | print(f"hfp_sink_node_present={'yes' if sink_ids else 'no'}") | AUDIO-ROUTING: success, rejection, unavailable/malformed and cleanup as applicable |
| 105 | print(f"default_sink_snapshot_available={'yes' if default_sink_id else 'no'}") | AUDIO-ROUTING: success, rejection, unavailable/malformed and cleanup as applicable |
| 106 | print(f"default_source_snapshot_available={'yes' if default_source_id else 'no'}") | AUDIO-ROUTING: success, rejection, unavailable/malformed and cleanup as applicable |
| 107 | print(f"default_sink_is_phone_hfp={'yes' if default_sink_id in sink_ids else 'no'}") | AUDIO-ROUTING: success, rejection, unavailable/malformed and cleanup as applicable |
| 108 | print(f"default_source_is_phone_hfp={'yes' if default_source_id in source_ids else 'no'}") | AUDIO-ROUTING: success, rejection, unavailable/malformed and cleanup as applicable |
| 109 | print(f"orphan_hfp_nodes_present={'yes' if hfp_nodes else 'no'}") | AUDIO-ROUTING: success, rejection, unavailable/malformed and cleanup as applicable |

## scripts/probe-bluetooth.sh

| Source line | Decision / method | Planned assertion family |
| --- | --- | --- |
| 8 | usage() { | BLUETOOTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 25 | while [[ $# -gt 0 ]]; do | BLUETOOTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 26 | case "$1" in | BLUETOOTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 27 | --device) | BLUETOOTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 28 | if [[ $# -lt 2 ]]; then | BLUETOOTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 35 | --host-only) | BLUETOOTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 40 | --help&#124;-h) | BLUETOOTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 44 | *) | BLUETOOTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 52 | if [[ -n "$DEVICE" ]] && [[ ! "$DEVICE" =~ ^([[:xdigit:]]{2}:){5}[[:xdigit:]]{2}$ ]]; then | BLUETOOTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 57 | command_present() { | BLUETOOTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 58 | if command -v "$1" >/dev/null 2>&1; then | BLUETOOTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 65 | bool_line() { | BLUETOOTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 70 | echo "probe_scope=host$([[ -n "$DEVICE" ]] && printf '+device')" | BLUETOOTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 76 | if command -v bluetoothctl >/dev/null 2>&1; then | BLUETOOTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 88 | bluetoothctl devices Paired 2>/dev/null &#124;&#124; | BLUETOOTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 89 | bluetoothctl paired-devices 2>/dev/null &#124;&#124; | BLUETOOTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 101 | if command -v systemctl >/dev/null 2>&1 && | BLUETOOTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 108 | if command -v busctl >/dev/null 2>&1 && | BLUETOOTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 115 | if command -v systemctl >/dev/null 2>&1 && | BLUETOOTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 122 | if [[ "$HOST_ONLY" == yes &#124;&#124; -z "$DEVICE" ]]; then | BLUETOOTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 126 | if ! command -v bluetoothctl >/dev/null 2>&1; then | BLUETOOTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 131 | info="$(bluetoothctl info "$DEVICE" 2>/dev/null &#124;&#124; true)" | BLUETOOTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 132 | if [[ -z "$info" ]]; then | BLUETOOTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 139 | property_is_yes() { | BLUETOOTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 141 | if grep -Eq "^[[:space:]]*$property:[[:space:]]+yes$" <<<"$info"; then | BLUETOOTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 154 | uuid_present() { | BLUETOOTH: success, rejection, unavailable/malformed and cleanup as applicable |
| 156 | if grep -Fq "$uuid" <<<"$lower_info"; then | BLUETOOTH: success, rejection, unavailable/malformed and cleanup as applicable |

## scripts/probe-call-audio-watch.sh

| Source line | Decision / method | Planned assertion family |
| --- | --- | --- |

## scripts/probe-hfp-audio.sh

| Source line | Decision / method | Planned assertion family |
| --- | --- | --- |
| 12 | usage() { | HFP-AUDIO: success, rejection, unavailable/malformed and cleanup as applicable |
| 29 | if [[ "${1:-}" == "--help" &#124;&#124; "${1:-}" == "-h" ]]; then | HFP-AUDIO: success, rejection, unavailable/malformed and cleanup as applicable |
| 34 | if [[ $# -ne 0 ]]; then | HFP-AUDIO: success, rejection, unavailable/malformed and cleanup as applicable |
| 40 | if [[ ! "$DEVICE" =~ ^([[:xdigit:]]{2}:){5}[[:xdigit:]]{2}$ ]]; then | HFP-AUDIO: success, rejection, unavailable/malformed and cleanup as applicable |
| 45 | if [[ ! "$CONNECT_TIMEOUT" =~ ^[1-9][0-9]*$ ]]; then | HFP-AUDIO: success, rejection, unavailable/malformed and cleanup as applicable |
| 50 | for command in bluetoothctl busctl grep head mktemp sed seq sleep timeout; do | HFP-AUDIO: success, rejection, unavailable/malformed and cleanup as applicable |
| 51 | if ! command -v "$command" >/dev/null 2>&1; then | HFP-AUDIO: success, rejection, unavailable/malformed and cleanup as applicable |
| 65 | cleanup() { | HFP-AUDIO: success, rejection, unavailable/malformed and cleanup as applicable |
| 70 | bool_line() { | HFP-AUDIO: success, rejection, unavailable/malformed and cleanup as applicable |
| 80 | info="$(bluetoothctl info "$DEVICE" 2>/dev/null &#124;&#124; true)" | HFP-AUDIO: success, rejection, unavailable/malformed and cleanup as applicable |
| 81 | if [[ -z "$info" ]]; then | HFP-AUDIO: success, rejection, unavailable/malformed and cleanup as applicable |
| 87 | if grep -Eq '^[[:space:]]*Paired:[[:space:]]+yes$' <<<"$info"; then | HFP-AUDIO: success, rejection, unavailable/malformed and cleanup as applicable |
| 94 | if grep -Fqi "$HFP_AG_UUID" <<<"$info"; then | HFP-AUDIO: success, rejection, unavailable/malformed and cleanup as applicable |
| 101 | if command -v systemctl >/dev/null 2>&1 && | HFP-AUDIO: success, rejection, unavailable/malformed and cleanup as applicable |
| 108 | if command -v systemctl >/dev/null 2>&1 && | HFP-AUDIO: success, rejection, unavailable/malformed and cleanup as applicable |
| 120 | if [[ $CONNECT_STATUS -eq 124 ]]; then | HFP-AUDIO: success, rejection, unavailable/malformed and cleanup as applicable |
| 123 | elif grep -Fq 'Connection successful' "$CONNECT_LOG"; then | HFP-AUDIO: success, rejection, unavailable/malformed and cleanup as applicable |
| 125 | elif grep -Eqi 'already connected&#124;connected: yes' "$CONNECT_LOG"; then | HFP-AUDIO: success, rejection, unavailable/malformed and cleanup as applicable |
| 132 | for _ in $(seq 1 50); do | HFP-AUDIO: success, rejection, unavailable/malformed and cleanup as applicable |
| 133 | if busctl --user call "$TELEPHONY_SERVICE" "$TELEPHONY_MANAGER"     org.ofono.Manager GetModems >"$MODEMS_REPLY" 2>/dev/null; then | HFP-AUDIO: success, rejection, unavailable/malformed and cleanup as applicable |
| 136 | grep -oE '/org/pipewire/Telephony/ag[0-9]+' "$MODEMS_REPLY" &#124;&#124; true | HFP-AUDIO: success, rejection, unavailable/malformed and cleanup as applicable |
| 140 | [[ -n "$AG_PATH" ]] && break | HFP-AUDIO: success, rejection, unavailable/malformed and cleanup as applicable |
| 145 | if [[ -z "$AG_PATH" ]]; then | HFP-AUDIO: success, rejection, unavailable/malformed and cleanup as applicable |
| 151 | if ! busctl --user introspect "$TELEPHONY_SERVICE" "$AG_PATH" >"$AG_INTROSPECT" 2>/dev/null; then | HFP-AUDIO: success, rejection, unavailable/malformed and cleanup as applicable |
| 156 | if grep -Fq "$TRANSPORT_IFACE" "$AG_INTROSPECT"; then | HFP-AUDIO: success, rejection, unavailable/malformed and cleanup as applicable |
| 163 | if grep -Fq 'Activate' "$AG_INTROSPECT"; then | HFP-AUDIO: success, rejection, unavailable/malformed and cleanup as applicable |
| 169 | if busctl --user get-property "$TELEPHONY_SERVICE" "$AG_PATH"   "$TRANSPORT_IFACE" State >"$STATE_REPLY" 2>/dev/null; then | HFP-AUDIO: success, rejection, unavailable/malformed and cleanup as applicable |
| 176 | if busctl --user get-property "$TELEPHONY_SERVICE" "$AG_PATH"   "$TRANSPORT_IFACE" Codec >"$CODEC_REPLY" 2>/dev/null; then | HFP-AUDIO: success, rejection, unavailable/malformed and cleanup as applicable |
| 183 | if busctl --user get-property "$TELEPHONY_SERVICE" "$AG_PATH"   "$TRANSPORT_IFACE" RejectSCO >"$REJECT_REPLY" 2>/dev/null; then | HFP-AUDIO: success, rejection, unavailable/malformed and cleanup as applicable |
| 197 | case "${CODEC:-}" in | HFP-AUDIO: success, rejection, unavailable/malformed and cleanup as applicable |
| 198 | 1) echo "transport_codec=cvsd" ;; | HFP-AUDIO: success, rejection, unavailable/malformed and cleanup as applicable |
| 199 | 2) echo "transport_codec=msbc" ;; | HFP-AUDIO: success, rejection, unavailable/malformed and cleanup as applicable |
| 200 | 3) echo "transport_codec=lc3_swb" ;; | HFP-AUDIO: success, rejection, unavailable/malformed and cleanup as applicable |
| 201 | *) echo "transport_codec=unknown" ;; | HFP-AUDIO: success, rejection, unavailable/malformed and cleanup as applicable |
| 204 | case "${REJECT_SCO:-}" in | HFP-AUDIO: success, rejection, unavailable/malformed and cleanup as applicable |
| 205 | true) | HFP-AUDIO: success, rejection, unavailable/malformed and cleanup as applicable |
| 209 | false) | HFP-AUDIO: success, rejection, unavailable/malformed and cleanup as applicable |
| 213 | *) | HFP-AUDIO: success, rejection, unavailable/malformed and cleanup as applicable |
| 219 | if [[ -n "$STATE" && -n "$CODEC" && -n "$REJECT_SCO" ]]; then | HFP-AUDIO: success, rejection, unavailable/malformed and cleanup as applicable |

## scripts/probe-hfp-call.sh

| Source line | Decision / method | Planned assertion family |
| --- | --- | --- |
| 13 | usage() { | HFP-CALL: success, rejection, unavailable/malformed and cleanup as applicable |
| 32 | while [[ $# -gt 0 ]]; do | HFP-CALL: success, rejection, unavailable/malformed and cleanup as applicable |
| 33 | case "$1" in | HFP-CALL: success, rejection, unavailable/malformed and cleanup as applicable |
| 34 | --dial) | HFP-CALL: success, rejection, unavailable/malformed and cleanup as applicable |
| 38 | --help&#124;-h) | HFP-CALL: success, rejection, unavailable/malformed and cleanup as applicable |
| 42 | *) | HFP-CALL: success, rejection, unavailable/malformed and cleanup as applicable |
| 50 | if [[ ! "$DEVICE" =~ ^([[:xdigit:]]{2}:){5}[[:xdigit:]]{2}$ ]]; then | HFP-CALL: success, rejection, unavailable/malformed and cleanup as applicable |
| 55 | if [[ ! "$OBSERVE_SECONDS" =~ ^[1-9][0-9]*$ ]]; then | HFP-CALL: success, rejection, unavailable/malformed and cleanup as applicable |
| 60 | if [[ "$DO_DIAL" == yes ]] && | HFP-CALL: success, rejection, unavailable/malformed and cleanup as applicable |
| 61 | [[ ! "$RECIPIENT" =~ ^[0-9+*#,A-D]{1,80}$ ]]; then | HFP-CALL: success, rejection, unavailable/malformed and cleanup as applicable |
| 66 | for command in bluetoothctl busctl grep head mktemp sleep seq timeout; do | HFP-CALL: success, rejection, unavailable/malformed and cleanup as applicable |
| 67 | if ! command -v "$command" >/dev/null 2>&1; then | HFP-CALL: success, rejection, unavailable/malformed and cleanup as applicable |
| 82 | cleanup() { | HFP-CALL: success, rejection, unavailable/malformed and cleanup as applicable |
| 86 | if [[ "$DIAL_ATTEMPTED" == yes && "$HANGUP_DONE" != yes && -n "$AG_PATH" ]]; then | HFP-CALL: success, rejection, unavailable/malformed and cleanup as applicable |
| 88 | if timeout 8s busctl --user call "$TELEPHONY_SERVICE" "$AG_PATH" \ | HFP-CALL: success, rejection, unavailable/malformed and cleanup as applicable |
| 101 | bool_line() { | HFP-CALL: success, rejection, unavailable/malformed and cleanup as applicable |
| 109 | info="$(bluetoothctl info "$DEVICE" 2>/dev/null &#124;&#124; true)" | HFP-CALL: success, rejection, unavailable/malformed and cleanup as applicable |
| 110 | if [[ -z "$info" ]] &#124;&#124; | HFP-CALL: success, rejection, unavailable/malformed and cleanup as applicable |
| 111 | ! grep -Eq '^[[:space:]]*Paired:[[:space:]]+yes$' <<<"$info"; then | HFP-CALL: success, rejection, unavailable/malformed and cleanup as applicable |
| 117 | if ! grep -Fqi "$HFP_AG_UUID" <<<"$info"; then | HFP-CALL: success, rejection, unavailable/malformed and cleanup as applicable |
| 128 | if [[ $CONNECT_STATUS -eq 124 ]]; then | HFP-CALL: success, rejection, unavailable/malformed and cleanup as applicable |
| 135 | for _ in $(seq 1 50); do | HFP-CALL: success, rejection, unavailable/malformed and cleanup as applicable |
| 136 | if busctl --user call "$TELEPHONY_SERVICE" "$TELEPHONY_MANAGER"     org.ofono.Manager GetModems >"$MODEMS_REPLY" 2>/dev/null; then | HFP-CALL: success, rejection, unavailable/malformed and cleanup as applicable |
| 139 | grep -oE '/org/pipewire/Telephony/ag[0-9]+' "$MODEMS_REPLY" &#124;&#124; true | HFP-CALL: success, rejection, unavailable/malformed and cleanup as applicable |
| 143 | [[ -n "$AG_PATH" ]] && break | HFP-CALL: success, rejection, unavailable/malformed and cleanup as applicable |
| 148 | if [[ -z "$AG_PATH" ]]; then | HFP-CALL: success, rejection, unavailable/malformed and cleanup as applicable |
| 154 | if ! busctl --user introspect "$TELEPHONY_SERVICE" "$AG_PATH" 2>/dev/null &#124; | HFP-CALL: success, rejection, unavailable/malformed and cleanup as applicable |
| 161 | if ! busctl --user call "$TELEPHONY_SERVICE" "$AG_PATH"   org.ofono.VoiceCallManager GetCalls >"$CALLS_REPLY" 2>/dev/null; then | HFP-CALL: success, rejection, unavailable/malformed and cleanup as applicable |
| 167 | if grep -qE '/org/pipewire/Telephony/ag[0-9]+/call[0-9]+' "$CALLS_REPLY"; then | HFP-CALL: success, rejection, unavailable/malformed and cleanup as applicable |
| 175 | if [[ "$DO_DIAL" != yes ]]; then | HFP-CALL: success, rejection, unavailable/malformed and cleanup as applicable |
| 194 | if [[ $DIAL_STATUS -ne 0 ]]; then | HFP-CALL: success, rejection, unavailable/malformed and cleanup as applicable |
| 203 | for _ in $(seq 1 "$((OBSERVE_SECONDS * 10))"); do | HFP-CALL: success, rejection, unavailable/malformed and cleanup as applicable |
| 204 | if busctl --user call "$TELEPHONY_SERVICE" "$AG_PATH"     org.ofono.VoiceCallManager GetCalls >"$CALLS_REPLY" 2>/dev/null && | HFP-CALL: success, rejection, unavailable/malformed and cleanup as applicable |
| 219 | if [[ $HANGUP_STATUS -eq 0 ]]; then | HFP-CALL: success, rejection, unavailable/malformed and cleanup as applicable |
| 231 | if [[ "$CALL_SEEN" == yes ]]; then | HFP-CALL: success, rejection, unavailable/malformed and cleanup as applicable |

## scripts/probe-hfp-sco.sh

| Source line | Decision / method | Planned assertion family |
| --- | --- | --- |
| 19 | usage() { | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 43 | while [[ $# -gt 0 ]]; do | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 44 | case "$1" in | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 45 | --dial) | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 49 | --help&#124;-h) | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 53 | *) | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 61 | if [[ ! "$DEVICE" =~ ^([[:xdigit:]]{2}:){5}[[:xdigit:]]{2}$ ]]; then | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 66 | for value_name in CONNECT_TIMEOUT STATE_TIMEOUT CALL_ACTIVE_TIMEOUT HUMAN_WINDOW; do | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 68 | if [[ ! "$value" =~ ^[1-9][0-9]*$ ]]; then | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 74 | if [[ "$DO_DIAL" == yes ]] && | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 75 | [[ ! "$RECIPIENT" =~ ^[0-9+*#,A-D]{1,80}$ ]]; then | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 80 | for command in bluetoothctl busctl cat grep head mktemp python3 pw-dump sed seq sleep timeout wpctl; do | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 81 | if ! command -v "$command" >/dev/null 2>&1; then | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 106 | cleanup() { | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 110 | if [[ "$DIAL_ATTEMPTED" == yes && "$HANGUP_DONE" != yes && -n "$AG_PATH" ]]; then | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 112 | if timeout 8s busctl --user call "$TELEPHONY_SERVICE" "$AG_PATH" \ | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 125 | bool_line() { | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 129 | read_transport_state() { | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 130 | if ! busctl --user get-property "$TELEPHONY_SERVICE" "$AG_PATH"     "$TRANSPORT_IFACE" State >"$STATE_REPLY" 2>/dev/null; then | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 136 | refresh_call_snapshot() { | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 140 | if ! busctl --user call "$TELEPHONY_SERVICE" "$AG_PATH" \ | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 147 | grep -oE '/org/pipewire/Telephony/ag[0-9]+/call[0-9]+' "$CALLS_REPLY" &#124;&#124; true | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 152 | if [[ -z "$CALL_PATH" ]]; then | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 156 | for state in active dialing alerting incoming waiting held disconnected; do | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 157 | if grep -Eq "\"State\"[[:space:]]+s[[:space:]]+\"$state\"" "$CALLS_REPLY"; then | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 163 | for iface in org.pipewire.Telephony.Call1 org.ofono.VoiceCall; do | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 164 | if busctl --user get-property "$TELEPHONY_SERVICE" "$CALL_PATH" \ | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 167 | if [[ -n "$CALL_STATE" ]]; then | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 176 | inspect_hfp_nodes() { | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 177 | if ! pw-dump >"$PW_DUMP" 2>/dev/null; then | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 187 | data = json.load(handle) | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 193 | for obj in data: | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 194 | if obj.get("type") != "PipeWire:Interface:Node": | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 198 | if props.get("api.bluez5.address") != device: | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 200 | if props.get("api.bluez5.profile") != "headset-head-unit": | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 204 | media_class = props.get("media.class") | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 205 | if media_class == "Audio/Source": | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 207 | elif media_class == "Audio/Sink": | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 210 | print(f"hfp_node_count={count}") | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 211 | print(f"hfp_source_node_present={'yes' if source else 'no'}") | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 212 | print(f"hfp_sink_node_present={'yes' if sink else 'no'}") | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 213 | print(f"hfp_nodes_ready={'yes' if count >= 2 and source and sink else 'no'}") | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 221 | info="$(bluetoothctl info "$DEVICE" 2>/dev/null &#124;&#124; true)" | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 222 | if [[ -z "$info" ]] &#124;&#124; | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 223 | ! grep -Eq '^[[:space:]]*Paired:[[:space:]]+yes$' <<<"$info"; then | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 229 | if ! grep -Fqi "$HFP_AG_UUID" <<<"$info"; then | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 240 | if [[ $CONNECT_STATUS -eq 124 ]]; then | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 243 | elif grep -Fq 'Connection successful' "$CONNECT_LOG"; then | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 245 | elif grep -Eqi 'already connected&#124;connected: yes' "$CONNECT_LOG"; then | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 251 | for _ in $(seq 1 50); do | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 252 | if busctl --user call "$TELEPHONY_SERVICE" "$TELEPHONY_MANAGER"     org.ofono.Manager GetModems >"$MODEMS_REPLY" 2>/dev/null; then | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 255 | grep -oE '/org/pipewire/Telephony/ag[0-9]+' "$MODEMS_REPLY" &#124;&#124; true | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 259 | [[ -n "$AG_PATH" ]] && break | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 264 | if [[ -z "$AG_PATH" ]]; then | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 270 | if ! busctl --user call "$TELEPHONY_SERVICE" "$AG_PATH"   org.ofono.VoiceCallManager GetCalls >"$CALLS_REPLY" 2>/dev/null; then | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 276 | if grep -qE '/org/pipewire/Telephony/ag[0-9]+/call[0-9]+' "$CALLS_REPLY"; then | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 284 | if ! busctl --user introspect "$TELEPHONY_SERVICE" "$AG_PATH" 2>/dev/null &#124; | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 291 | if ! busctl --user introspect "$TELEPHONY_SERVICE" "$AG_PATH" 2>/dev/null &#124; | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 298 | if ! busctl --user get-property "$TELEPHONY_SERVICE" "$AG_PATH"   "$TRANSPORT_IFACE" RejectSCO >"$REJECT_REPLY" 2>/dev/null; then | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 304 | if grep -Fq 'b true' "$REJECT_REPLY"; then | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 309 | elif grep -Fq 'b false' "$REJECT_REPLY"; then | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 317 | INITIAL_STATE="$(read_transport_state &#124;&#124; true)" | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 320 | if [[ "$DO_DIAL" != yes ]]; then | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 340 | if [[ $DIAL_STATUS -ne 0 ]]; then | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 349 | for _ in $(seq 1 "$((STATE_TIMEOUT * 10))"); do | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 350 | if refresh_call_snapshot && [[ -n "$CALL_PATH" ]]; then | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 358 | if [[ "$CALL_SEEN" != yes ]]; then | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 367 | for _ in $(seq 1 "$((CALL_ACTIVE_TIMEOUT * 10))"); do | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 368 | if refresh_call_snapshot; then | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 370 | if [[ "$LAST_CALL_STATE" == active ]]; then | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 381 | if [[ "$CALL_ACTIVE_SEEN" != yes ]]; then | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 390 | TRANSPORT_STATE_BEFORE_ACTIVATE="$(read_transport_state &#124;&#124; true)" | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 399 | case "$TRANSPORT_STATE_BEFORE_ACTIVATE" in | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 400 | active) | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 405 | pending) | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 410 | for _ in $(seq 1 "$((STATE_TIMEOUT * 10))"); do | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 411 | LAST_STATE="$(read_transport_state &#124;&#124; true)" | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 412 | if [[ "$LAST_STATE" == active ]]; then | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 416 | [[ "$LAST_STATE" == idle &#124;&#124; "$LAST_STATE" == error ]] && break | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 420 | idle) | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 430 | if [[ $ACTIVATE_STATUS -ne 0 ]]; then | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 435 | grep -oE 'org\.pipewire\.Telephony\.Error\.(InvalidState&#124;InvalidFormat&#124;NotSupported&#124;InProgress&#124;Failed&#124;CME)&#124;org\.freedesktop\.DBus\.Error\.(InvalidArgs&#124;Failed&#124;NoReply&#124;Timeout&#124;AccessDenied&#124;ServiceUnknown)' "$ACTIVATE_REPLY" &#124;&#124; | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 439 | if [[ -z "$ACTIVATE_ERROR_CLASS" ]]; then | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 440 | if grep -Eqi 'timed out&#124;timeout' "$ACTIVATE_REPLY"; then | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 442 | elif grep -Eqi 'invalid state&#124;already active' "$ACTIVATE_REPLY"; then | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 449 | LAST_STATE="$(read_transport_state &#124;&#124; true)" | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 453 | for _ in $(seq 1 15); do | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 454 | [[ "$LAST_STATE" == active ]] && { ACTIVE_SEEN=yes; break; } | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 455 | [[ "$LAST_STATE" == error ]] && break | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 457 | LAST_STATE="$(read_transport_state &#124;&#124; true)" | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 459 | if [[ "$LAST_STATE" == active ]]; then | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 468 | *) | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 474 | if [[ "$ACTIVATE_INVOKED" != yes ]]; then | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 478 | if [[ "$ACTIVE_SEEN" != yes && "$ACTIVATE_STATUS" != not_called && "$ACTIVATE_STATUS" != 0 ]]; then | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 486 | if [[ "$ACTIVE_SEEN" != yes && "$ACTIVATE_STATUS" != not_called && "$ACTIVATE_STATUS" == 0 ]]; then | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 487 | for _ in $(seq 1 "$((STATE_TIMEOUT * 10))"); do | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 488 | LAST_STATE="$(read_transport_state &#124;&#124; true)" | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 489 | if [[ "$LAST_STATE" == active ]]; then | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 493 | [[ "$LAST_STATE" == error ]] && break | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 502 | if [[ "$ACTIVE_SEEN" != yes ]]; then | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 509 | for _ in $(seq 1 "$((STATE_TIMEOUT * 10))"); do | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 510 | if inspect_hfp_nodes && grep -Fq 'hfp_nodes_ready=yes' "$NODE_RESULT"; then | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 517 | if [[ -s "$NODE_RESULT" ]]; then | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 528 | if [[ "$NODES_READY" != yes ]]; then | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 543 | if [[ $HANGUP_STATUS -ne 0 ]]; then | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |
| 553 | if [[ "$ACTIVATE_RESULT" == error_but_transport_active ]]; then | HFP-SCO: success, rejection, unavailable/malformed and cleanup as applicable |

## scripts/probe-hfp.sh

| Source line | Decision / method | Planned assertion family |
| --- | --- | --- |
| 11 | usage() { | HFP: success, rejection, unavailable/malformed and cleanup as applicable |
| 25 | if [[ "${1:-}" == "--help" &#124;&#124; "${1:-}" == "-h" ]]; then | HFP: success, rejection, unavailable/malformed and cleanup as applicable |
| 30 | if [[ $# -ne 0 ]]; then | HFP: success, rejection, unavailable/malformed and cleanup as applicable |
| 36 | if [[ ! "$DEVICE" =~ ^([[:xdigit:]]{2}:){5}[[:xdigit:]]{2}$ ]]; then | HFP: success, rejection, unavailable/malformed and cleanup as applicable |
| 41 | if [[ ! "$CONNECT_TIMEOUT" =~ ^[1-9][0-9]*$ ]]; then | HFP: success, rejection, unavailable/malformed and cleanup as applicable |
| 46 | for command in bluetoothctl busctl grep awk sed head tail tr mktemp timeout seq sleep; do | HFP: success, rejection, unavailable/malformed and cleanup as applicable |
| 47 | if ! command -v "$command" >/dev/null 2>&1; then | HFP: success, rejection, unavailable/malformed and cleanup as applicable |
| 61 | cleanup() { | HFP: success, rejection, unavailable/malformed and cleanup as applicable |
| 66 | bool_line() { | HFP: success, rejection, unavailable/malformed and cleanup as applicable |
| 75 | info="$(bluetoothctl info "$DEVICE" 2>/dev/null &#124;&#124; true)" | HFP: success, rejection, unavailable/malformed and cleanup as applicable |
| 76 | if [[ -z "$info" ]]; then | HFP: success, rejection, unavailable/malformed and cleanup as applicable |
| 82 | if grep -Eq '^[[:space:]]*Paired:[[:space:]]+yes$' <<<"$info"; then | HFP: success, rejection, unavailable/malformed and cleanup as applicable |
| 89 | if grep -Fqi "$HFP_AG_UUID" <<<"$info"; then | HFP: success, rejection, unavailable/malformed and cleanup as applicable |
| 96 | if command -v systemctl >/dev/null 2>&1 && | HFP: success, rejection, unavailable/malformed and cleanup as applicable |
| 103 | if command -v systemctl >/dev/null 2>&1 && | HFP: success, rejection, unavailable/malformed and cleanup as applicable |
| 110 | if command -v pipewire >/dev/null 2>&1; then | HFP: success, rejection, unavailable/malformed and cleanup as applicable |
| 117 | if command -v wireplumber >/dev/null 2>&1; then | HFP: success, rejection, unavailable/malformed and cleanup as applicable |
| 124 | if busctl --user introspect "$TELEPHONY_SERVICE" "$TELEPHONY_MANAGER" >"$MANAGER_INTROSPECT" 2>/dev/null; then | HFP: success, rejection, unavailable/malformed and cleanup as applicable |
| 130 | if grep -Fq 'org.ofono.Manager' "$MANAGER_INTROSPECT" 2>/dev/null && | HFP: success, rejection, unavailable/malformed and cleanup as applicable |
| 146 | if [[ $CONNECT_STATUS -eq 124 ]]; then | HFP: success, rejection, unavailable/malformed and cleanup as applicable |
| 148 | elif grep -Fq 'Connection successful' "$CONNECT_LOG"; then | HFP: success, rejection, unavailable/malformed and cleanup as applicable |
| 150 | elif grep -Eqi 'already connected&#124;connected: yes' "$CONNECT_LOG"; then | HFP: success, rejection, unavailable/malformed and cleanup as applicable |
| 157 | for _ in $(seq 1 50); do | HFP: success, rejection, unavailable/malformed and cleanup as applicable |
| 158 | if busctl --user call "$TELEPHONY_SERVICE" "$TELEPHONY_MANAGER"     org.ofono.Manager GetModems >"$MODEMS_REPLY" 2>/dev/null; then | HFP: success, rejection, unavailable/malformed and cleanup as applicable |
| 161 | grep -oE '/org/pipewire/Telephony/ag[0-9]+' "$MODEMS_REPLY" &#124;&#124; | HFP: success, rejection, unavailable/malformed and cleanup as applicable |
| 166 | if [[ -n "$AG_PATH" ]]; then | HFP: success, rejection, unavailable/malformed and cleanup as applicable |
| 173 | if [[ -n "$AG_PATH" ]]; then | HFP: success, rejection, unavailable/malformed and cleanup as applicable |
| 181 | if [[ -n "$AG_PATH" ]] && | HFP: success, rejection, unavailable/malformed and cleanup as applicable |
| 183 | if grep -Fq 'org.pipewire.Telephony.AudioGateway1' "$AG_INTROSPECT" && | HFP: success, rejection, unavailable/malformed and cleanup as applicable |
| 184 | grep -Fq 'Dial' "$AG_INTROSPECT" && | HFP: success, rejection, unavailable/malformed and cleanup as applicable |
| 185 | grep -Fq 'HangupAll' "$AG_INTROSPECT" && | HFP: success, rejection, unavailable/malformed and cleanup as applicable |
| 192 | if grep -Fq 'org.ofono.VoiceCallManager' "$AG_INTROSPECT" && | HFP: success, rejection, unavailable/malformed and cleanup as applicable |
| 203 | if [[ -n "$AG_PATH" ]] && | HFP: success, rejection, unavailable/malformed and cleanup as applicable |
| 206 | if grep -qE '/org/pipewire/Telephony/ag[0-9]+/call[0-9]+' "$CALLS_REPLY"; then | HFP: success, rejection, unavailable/malformed and cleanup as applicable |
| 216 | if command -v pw-dump >/dev/null 2>&1 && | HFP: success, rejection, unavailable/malformed and cleanup as applicable |
| 218 | if grep -Fqi "$DEVICE" "$PW_DUMP"; then | HFP: success, rejection, unavailable/malformed and cleanup as applicable |

## scripts/probe-map-events.sh

| Source line | Decision / method | Planned assertion family |
| --- | --- | --- |
| 9 | usage() { | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 34 | while [[ $# -gt 0 ]]; do | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 35 | case "$1" in | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 36 | --help&#124;-h) | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 40 | *) | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 48 | if [[ ! "$DEVICE" =~ ^([[:xdigit:]]{2}:){5}[[:xdigit:]]{2}$ ]]; then | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 53 | for value_name in EVENT_TIMEOUT CONNECT_TIMEOUT; do | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 55 | if [[ ! "$value" =~ ^[1-9][0-9]*$ ]]; then | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 61 | for command in busctl bluetoothctl obexctl stdbuf mktemp; do | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 62 | if ! command -v "$command" >/dev/null 2>&1; then | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 72 | if ! busctl --user list 2>/dev/null &#124; awk '{print $1}' &#124; grep -Fxq org.bluez.obex; then | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 78 | if ! bluetoothctl info "$DEVICE" 2>/dev/null &#124; grep -Eq '^[[:space:]]*Paired:[[:space:]]+yes$'; then | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 84 | if bluetoothctl show 2>/dev/null &#124; | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 103 | cleanup() { | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 106 | if [[ -n "$OBEX_FD" ]]; then | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 107 | printf 'disconnect\nquit\n' >&"$OBEX_FD" 2>/dev/null &#124;&#124; true | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 108 | exec {OBEX_FD}>&- 2>/dev/null &#124;&#124; true | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 111 | if [[ -n "$OBEX_PID" ]] && kill -0 "$OBEX_PID" 2>/dev/null; then | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 112 | for _ in 1 2 3 4 5; do | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 113 | kill -0 "$OBEX_PID" 2>/dev/null &#124;&#124; break | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 116 | kill "$OBEX_PID" 2>/dev/null &#124;&#124; true | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 117 | wait "$OBEX_PID" 2>/dev/null &#124;&#124; true | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 120 | if [[ -n "$MONITOR_PID" ]] && kill -0 "$MONITOR_PID" 2>/dev/null; then | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 121 | kill "$MONITOR_PID" 2>/dev/null &#124;&#124; true | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 122 | wait "$MONITOR_PID" 2>/dev/null &#124;&#124; true | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 136 | if ! kill -0 "$MONITOR_PID" 2>/dev/null; then | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 146 | wait_for_log() { | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 152 | while (( elapsed < timeout_seconds * 10 )); do | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 153 | if grep -Eq "$pattern" "$file" 2>/dev/null; then | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 157 | ((elapsed += 1)) | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 163 | if ! wait_for_log "$OBEX_LOG" 'Client .*/org/bluez/obex&#124;\[NEW\].*Client' 5; then | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 171 | if ! wait_for_log "$OBEX_LOG" 'Connection successful&#124;Failed to connect' "$CONNECT_TIMEOUT"; then | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 177 | if grep -Fq 'Failed to connect' "$OBEX_LOG"; then | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 188 | if [[ -z "$SESSION_PATH" ]]; then | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 194 | if ! wait_for_log "$OBEX_LOG" 'MessageAccess /org/bluez/obex/client/session&#124;\[NEW\].*MessageAccess' 2; then | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 206 | if wait_for_log "$MONITOR_LOG" 'org\.bluez\.obex\.Transfer1' 3; then | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 209 | for _ in {1..30}; do | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 210 | if grep -Eqi 'Status.*complete&#124;complete.*Status' "$MONITOR_LOG"; then | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 214 | if grep -Eqi 'Status.*error&#124;error.*Status' "$MONITOR_LOG"; then | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 221 | if [[ "$registration_transfer_status" == not_seen ]]; then | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 232 | grep -Ec 'org\.bluez\.obex\.Message1' "$MONITOR_LOG" 2>/dev/null &#124;&#124; true | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 235 | grep -Ec '\[NEW\].*Message /org/bluez/obex/client/session[0-9]+/message[0-9]+' "$OBEX_LOG" 2>/dev/null &#124;&#124; true | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 240 | while (( elapsed < EVENT_TIMEOUT * 10 )); do | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 242 | grep -Ec 'org\.bluez\.obex\.Message1' "$MONITOR_LOG" 2>/dev/null &#124;&#124; true | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 245 | grep -Ec '\[NEW\].*Message /org/bluez/obex/client/session[0-9]+/message[0-9]+' "$OBEX_LOG" 2>/dev/null &#124;&#124; true | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 248 | if (( current_monitor_messages > baseline_monitor_messages &#124;&#124; | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 254 | if ! kill -0 "$OBEX_PID" 2>/dev/null; then | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 261 | if ! kill -0 "$MONITOR_PID" 2>/dev/null; then | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 269 | ((elapsed += 1)) | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 274 | if [[ "$event_observed" == yes ]]; then | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 277 | if [[ "$registration_transfer_status" == complete ]]; then | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |
| 284 | if [[ "$registration_transfer_status" != complete ]]; then | MAP-EVENTS: success, rejection, unavailable/malformed and cleanup as applicable |

## scripts/probe-map-sdp.sh

| Source line | Decision / method | Planned assertion family |
| --- | --- | --- |
| 7 | usage() { | MAP-SDP: success, rejection, unavailable/malformed and cleanup as applicable |
| 23 | while [[ $# -gt 0 ]]; do | MAP-SDP: success, rejection, unavailable/malformed and cleanup as applicable |
| 24 | case "$1" in | MAP-SDP: success, rejection, unavailable/malformed and cleanup as applicable |
| 25 | --help&#124;-h) | MAP-SDP: success, rejection, unavailable/malformed and cleanup as applicable |
| 29 | *) | MAP-SDP: success, rejection, unavailable/malformed and cleanup as applicable |
| 37 | if [[ ! "$DEVICE" =~ ^([[:xdigit:]]{2}:){5}[[:xdigit:]]{2}$ ]]; then | MAP-SDP: success, rejection, unavailable/malformed and cleanup as applicable |
| 42 | for command in sdptool timeout mktemp; do | MAP-SDP: success, rejection, unavailable/malformed and cleanup as applicable |
| 43 | if ! command -v "$command" >/dev/null 2>&1; then | MAP-SDP: success, rejection, unavailable/malformed and cleanup as applicable |
| 60 | if [[ $SDP_STATUS -eq 124 ]]; then | MAP-SDP: success, rejection, unavailable/malformed and cleanup as applicable |
| 64 | elif [[ $SDP_STATUS -ne 0 ]]; then | MAP-SDP: success, rejection, unavailable/malformed and cleanup as applicable |
| 72 | if grep -Eqi '<attribute[^>]+id="0x0315"&#124;<attribute[^>]+id="0x315"' "$SDP_OUT"; then | MAP-SDP: success, rejection, unavailable/malformed and cleanup as applicable |
| 78 | if grep -Eqi '<attribute[^>]+id="0x0316"&#124;<attribute[^>]+id="0x316"' "$SDP_OUT"; then | MAP-SDP: success, rejection, unavailable/malformed and cleanup as applicable |
| 84 | if grep -Eqi '<attribute[^>]+id="0x0317"&#124;<attribute[^>]+id="0x317"' "$SDP_OUT"; then | MAP-SDP: success, rejection, unavailable/malformed and cleanup as applicable |
| 90 | if grep -Eqi 'uuid[^>]+value="0x1132"&#124;uuid[^>]+value="00001132' "$SDP_OUT"; then | MAP-SDP: success, rejection, unavailable/malformed and cleanup as applicable |

## scripts/probe-map-send.sh

| Source line | Decision / method | Planned assertion family |
| --- | --- | --- |
| 12 | usage() { | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 33 | while [[ $# -gt 0 ]]; do | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 34 | case "$1" in | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 35 | --send) | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 39 | --help&#124;-h) | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 43 | *) | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 51 | if [[ ! "$DEVICE" =~ ^([[:xdigit:]]{2}:){5}[[:xdigit:]]{2}$ ]]; then | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 56 | if [[ ! "$RECIPIENT" =~ ^\+[1-9][0-9]{6,14}$ ]]; then | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 61 | for value_name in CONNECT_TIMEOUT TRANSFER_TIMEOUT; do | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 63 | if [[ ! "$value" =~ ^[1-9][0-9]*$ ]]; then | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 69 | for command in busctl bluetoothctl obexctl stdbuf mktemp wc tail grep sed od tr; do | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 70 | if ! command -v "$command" >/dev/null 2>&1; then | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 80 | if ! busctl --user list 2>/dev/null &#124; awk '{print $1}' &#124; grep -Fxq org.bluez.obex; then | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 86 | if ! bluetoothctl info "$DEVICE" 2>/dev/null &#124; grep -Eq '^[[:space:]]*Paired:[[:space:]]+yes$'; then | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 105 | cleanup() { | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 108 | if [[ -n "$OBEX_FD" ]]; then | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 109 | printf 'disconnect\nquit\n' >&"$OBEX_FD" 2>/dev/null &#124;&#124; true | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 110 | exec {OBEX_FD}>&- 2>/dev/null &#124;&#124; true | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 113 | if [[ -n "$OBEX_PID" ]] && kill -0 "$OBEX_PID" 2>/dev/null; then | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 114 | for _ in 1 2 3 4 5; do | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 115 | kill -0 "$OBEX_PID" 2>/dev/null &#124;&#124; break | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 118 | kill "$OBEX_PID" 2>/dev/null &#124;&#124; true | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 119 | wait "$OBEX_PID" 2>/dev/null &#124;&#124; true | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 122 | if [[ -n "$MONITOR_PID" ]] && kill -0 "$MONITOR_PID" 2>/dev/null; then | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 123 | kill "$MONITOR_PID" 2>/dev/null &#124;&#124; true | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 124 | wait "$MONITOR_PID" 2>/dev/null &#124;&#124; true | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 136 | if ! kill -0 "$MONITOR_PID" 2>/dev/null; then | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 146 | wait_for_log() { | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 152 | while (( elapsed < timeout_seconds * 10 )); do | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 153 | if grep -Eq "$pattern" "$file" 2>/dev/null; then | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 156 | if [[ "$file" == "$OBEX_LOG" ]] && ! kill -0 "$OBEX_PID" 2>/dev/null; then | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 160 | ((elapsed += 1)) | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 166 | if ! wait_for_log "$OBEX_LOG" 'Client .*/org/bluez/obex&#124;\[NEW\].*Client' 5; then | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 174 | if ! wait_for_log "$OBEX_LOG" 'Connection successful&#124;Failed to connect' "$CONNECT_TIMEOUT"; then | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 180 | if grep -Fq 'Failed to connect' "$OBEX_LOG"; then | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 191 | if [[ -z "$SESSION_PATH" ]]; then | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 197 | if ! wait_for_log "$OBEX_LOG" 'MessageAccess /org/bluez/obex/client/session&#124;\[NEW\].*MessageAccess' 2; then | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 205 | if busctl --user get-property org.bluez.obex "$SESSION_PATH"   org.bluez.obex.MessageAccess1 SupportedTypes >"$SUPPORTED_TYPES" 2>/dev/null && | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 213 | if ! busctl --user call org.bluez.obex "$SESSION_PATH"   org.bluez.obex.MessageAccess1 SetFolder s telecom >/dev/null 2>&1; then | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 219 | if ! busctl --user call org.bluez.obex "$SESSION_PATH"   org.bluez.obex.MessageAccess1 SetFolder s msg >/dev/null 2>&1; then | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 255 | if ! grep -Fqx $'BEGIN:MSG\r' "$BMSG_FILE" &#124;&#124; | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 256 | ! grep -Fqx $'END:MSG\r' "$BMSG_FILE" &#124;&#124; | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 257 | ! grep -Fqx $'END:BBODY\r' "$BMSG_FILE" &#124;&#124; | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 258 | [[ "$(tail -c 2 "$BMSG_FILE" &#124; od -An -t x1 &#124; tr -d '[:space:]')" != "0d0a" ]]; then | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 270 | if [[ "$DO_SEND" != yes ]]; then | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 286 | if [[ $PUSH_STATUS -ne 0 ]]; then | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 299 | if [[ -n "$TRANSFER_PATH" ]]; then | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 307 | while (( elapsed < TRANSFER_TIMEOUT * 10 )); do | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 309 | tail -n "+$((MONITOR_BASELINE + 1))" "$MONITOR_LOG" >"$NEW_LOG" 2>/dev/null &#124;&#124; true | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 311 | if grep -A 8 -F 'STRING "Status"' "$NEW_LOG" &#124; | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 317 | if grep -A 8 -F 'STRING "Status"' "$NEW_LOG" &#124; | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 323 | if ! kill -0 "$OBEX_PID" 2>/dev/null; then | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 329 | ((elapsed += 1)) | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 334 | case "$transfer_result" in | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 335 | complete) | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 339 | error) | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 344 | session_lost) | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |
| 349 | *) | MAP-SEND: success, rejection, unavailable/malformed and cleanup as applicable |

## scripts/probe-mns.sh

| Source line | Decision / method | Planned assertion family |
| --- | --- | --- |
| 7 | command_present() { | MNS: success, rejection, unavailable/malformed and cleanup as applicable |
| 8 | if command -v "$1" >/dev/null 2>&1; then | MNS: success, rejection, unavailable/malformed and cleanup as applicable |
| 15 | bool_line() { | MNS: success, rejection, unavailable/malformed and cleanup as applicable |
| 25 | if command -v dpkg-query >/dev/null 2>&1; then | MNS: success, rejection, unavailable/malformed and cleanup as applicable |
| 26 | package_version="$(dpkg-query -W -f='${Version}' bluez-obexd 2>/dev/null &#124;&#124; true)" | MNS: success, rejection, unavailable/malformed and cleanup as applicable |
| 32 | if command -v busctl >/dev/null 2>&1 && | MNS: success, rejection, unavailable/malformed and cleanup as applicable |
| 39 | if command -v busctl >/dev/null 2>&1 && | MNS: success, rejection, unavailable/malformed and cleanup as applicable |
| 48 | head -n 1 &#124;&#124; | MNS: success, rejection, unavailable/malformed and cleanup as applicable |
| 52 | if [[ -n "$OBEX_PID" && -r "/proc/$OBEX_PID/exe" ]]; then | MNS: success, rejection, unavailable/malformed and cleanup as applicable |
| 54 | OBEX_EXE="$(readlink -f "/proc/$OBEX_PID/exe" 2>/dev/null &#124;&#124; true)" | MNS: success, rejection, unavailable/malformed and cleanup as applicable |
| 60 | if [[ -n "$OBEX_PID" && -r "/proc/$OBEX_PID/cmdline" ]]; then | MNS: success, rejection, unavailable/malformed and cleanup as applicable |
| 62 | if grep -Eq -- '--noplugin([=[:space:]][^ ]*,?)*mns&#124;--noplugin[=[:space:]]+mns' <<<"$CMDLINE"; then | MNS: success, rejection, unavailable/malformed and cleanup as applicable |
| 71 | if [[ -n "$OBEX_EXE" && -r "$OBEX_EXE" ]] && command -v strings >/dev/null 2>&1; then | MNS: success, rejection, unavailable/malformed and cleanup as applicable |
| 77 | if grep -Fq 'x-bt/MAP-NotificationRegistration' "$STRINGS_OUT"; then | MNS: success, rejection, unavailable/malformed and cleanup as applicable |
| 83 | if grep -Fq 'x-bt/MAP-event-report' "$STRINGS_OUT"; then | MNS: success, rejection, unavailable/malformed and cleanup as applicable |
| 89 | if grep -Fq 'Message Notification server' "$STRINGS_OUT"; then | MNS: success, rejection, unavailable/malformed and cleanup as applicable |
| 95 | if grep -Fq 'x-bt/MAP-event-report' "$STRINGS_OUT" &#124;&#124; | MNS: success, rejection, unavailable/malformed and cleanup as applicable |
| 110 | if command -v bluetoothctl >/dev/null 2>&1 && | MNS: success, rejection, unavailable/malformed and cleanup as applicable |
| 119 | if command -v sdptool >/dev/null 2>&1; then | MNS: success, rejection, unavailable/malformed and cleanup as applicable |
| 127 | if [[ $SDP_STATUS -eq 0 ]]; then | MNS: success, rejection, unavailable/malformed and cleanup as applicable |
| 130 | if grep -Eqi 'Message Notification&#124;0x1133&#124;00001133-0000-1000-8000-00805f9b34fb' "$SDP_OUT"; then | MNS: success, rejection, unavailable/malformed and cleanup as applicable |
| 137 | if grep -Eqi 'permission&#124;not permitted&#124;access denied' "$SDP_OUT"; then | MNS: success, rejection, unavailable/malformed and cleanup as applicable |
| 139 | elif grep -Eqi 'connection refused&#124;failed to connect&#124;no such file&#124;not available&#124;not found' "$SDP_OUT"; then | MNS: success, rejection, unavailable/malformed and cleanup as applicable |
| 153 | if [[ "${OBEX_EXE:-}" != "" ]] && | MNS: success, rejection, unavailable/malformed and cleanup as applicable |
| 154 | command -v strings >/dev/null 2>&1 && | MNS: success, rejection, unavailable/malformed and cleanup as applicable |
| 155 | strings "$OBEX_EXE" &#124; grep -Fq 'x-bt/MAP-NotificationRegistration' && | MNS: success, rejection, unavailable/malformed and cleanup as applicable |
| 156 | strings "$OBEX_EXE" &#124; grep -Fq 'x-bt/MAP-event-report' && | MNS: success, rejection, unavailable/malformed and cleanup as applicable |

## scripts/probe-obex-read.sh

| Source line | Decision / method | Planned assertion family |
| --- | --- | --- |
| 9 | usage() { | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 26 | while [[ $# -gt 0 ]]; do | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 27 | case "$1" in | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 28 | --device) | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 29 | [[ $# -ge 2 ]] &#124;&#124; { echo "--device requires a Bluetooth address." >&2; exit 2; } | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 33 | --target) | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 34 | [[ $# -ge 2 ]] &#124;&#124; { echo "--target requires map or pbap." >&2; exit 2; } | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 38 | --help&#124;-h) | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 42 | *) | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 50 | if [[ ! "$DEVICE" =~ ^([[:xdigit:]]{2}:){5}[[:xdigit:]]{2}$ ]]; then | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 55 | if [[ ! "$CONNECT_TIMEOUT" =~ ^[1-9][0-9]*$ ]]; then | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 60 | case "$TARGET" in | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 61 | map) | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 65 | pbap) | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 69 | *) | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 75 | for command in busctl bluetoothctl obexctl stdbuf mktemp; do | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 76 | if ! command -v "$command" >/dev/null 2>&1; then | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 87 | if ! busctl --user list 2>/dev/null &#124; awk '{print $1}' &#124; grep -Fxq org.bluez.obex; then | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 93 | if ! bluetoothctl info "$DEVICE" 2>/dev/null &#124; grep -Eq '^[[:space:]]*Paired:[[:space:]]+yes$'; then | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 108 | cleanup() { | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 111 | if [[ -n "$OBEX_FD" ]]; then | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 112 | printf 'disconnect\nquit\n' >&"$OBEX_FD" 2>/dev/null &#124;&#124; true | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 113 | exec {OBEX_FD}>&- 2>/dev/null &#124;&#124; true | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 116 | if [[ -n "$OBEX_PID" ]] && kill -0 "$OBEX_PID" 2>/dev/null; then | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 117 | for _ in 1 2 3 4 5; do | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 118 | kill -0 "$OBEX_PID" 2>/dev/null &#124;&#124; break | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 121 | kill "$OBEX_PID" 2>/dev/null &#124;&#124; true | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 122 | wait "$OBEX_PID" 2>/dev/null &#124;&#124; true | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 134 | wait_for_log() { | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 139 | while (( elapsed < timeout_seconds * 10 )); do | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 140 | if grep -Eq "$pattern" "$OBEX_LOG" 2>/dev/null; then | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 143 | if ! kill -0 "$OBEX_PID" 2>/dev/null; then | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 147 | ((elapsed += 1)) | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 153 | if ! wait_for_log 'Client .*/org/bluez/obex&#124;\[NEW\].*Client' 5; then | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 161 | if ! wait_for_log 'Connection successful&#124;Failed to connect' "$CONNECT_TIMEOUT"; then | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 167 | if grep -Fq 'Failed to connect' "$OBEX_LOG"; then | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 178 | if [[ -z "$SESSION_PATH" ]]; then | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 184 | if ! wait_for_log "\[NEW\].*$EXPECTED_PROXY_LABEL&#124;$EXPECTED_PROXY_LABEL /org/bluez/obex/client/session" 2; then | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 190 | if ! busctl --user introspect   org.bluez.obex   "$SESSION_PATH"   "$EXPECTED_INTERFACE" >/dev/null 2>&1; then | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 198 | array_count() { | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 203 | dbus_error_name() { | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 205 | grep -Eo 'org\.bluez\.obex\.Error\.[A-Za-z]+' "$file" &#124; head -n 1 &#124;&#124; true | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 208 | call_to_file() { | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 220 | if [[ "$TARGET" == "map" ]]; then | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 222 | if call_to_file "$FOLDERS_OUT"     org.bluez.obex "$SESSION_PATH" org.bluez.obex.MessageAccess1     ListFolders 'a{sv}' 1 MaxCount q 16; then | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 225 | if [[ "$count" == "unknown" ]]; then | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 227 | elif (( count > 0 )); then | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 240 | if call_to_file "$TELECOM_OUT"     org.bluez.obex "$SESSION_PATH" org.bluez.obex.MessageAccess1     SetFolder s telecom; then | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 250 | if call_to_file "$MSG_OUT"     org.bluez.obex "$SESSION_PATH" org.bluez.obex.MessageAccess1     SetFolder s msg; then | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 260 | if call_to_file "$MESSAGES_OUT"     org.bluez.obex "$SESSION_PATH" org.bluez.obex.MessageAccess1     ListMessages 'sa{sv}' inbox 2 MaxCount q 1 Fields as 1 type; then | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 263 | if [[ "$count" == "unknown" ]]; then | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 265 | elif (( count > 0 )); then | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 282 | if call_to_file "$SELECT_OUT"   org.bluez.obex "$SESSION_PATH" org.bluez.obex.PhonebookAccess1   Select ss int pb; then | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 292 | if call_to_file "$SIZE_OUT"   org.bluez.obex "$SESSION_PATH" org.bluez.obex.PhonebookAccess1 GetSize; then | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 294 | size="$(awk 'NR == 1 && $1 == "q" && $2 ~ /^[0-9]+$/ { print $2 }' "$SIZE_OUT")" | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 295 | if [[ -z "$size" ]]; then | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 297 | elif (( size > 0 )); then | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 310 | if call_to_file "$LIST_OUT"   org.bluez.obex "$SESSION_PATH" org.bluez.obex.PhonebookAccess1   List 'a{sv}' 1 MaxCount q 1; then | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 313 | if [[ "$count" == "unknown" ]]; then | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |
| 315 | elif (( count > 0 )); then | OBEX-READ: success, rejection, unavailable/malformed and cleanup as applicable |

## scripts/probe-obex-session.sh

| Source line | Decision / method | Planned assertion family |
| --- | --- | --- |
| 9 | usage() { | OBEX-SESSION: success, rejection, unavailable/malformed and cleanup as applicable |
| 28 | while [[ $# -gt 0 ]]; do | OBEX-SESSION: success, rejection, unavailable/malformed and cleanup as applicable |
| 29 | case "$1" in | OBEX-SESSION: success, rejection, unavailable/malformed and cleanup as applicable |
| 30 | --device) | OBEX-SESSION: success, rejection, unavailable/malformed and cleanup as applicable |
| 31 | [[ $# -ge 2 ]] &#124;&#124; { echo "--device requires a Bluetooth address." >&2; exit 2; } | OBEX-SESSION: success, rejection, unavailable/malformed and cleanup as applicable |
| 35 | --target) | OBEX-SESSION: success, rejection, unavailable/malformed and cleanup as applicable |
| 36 | [[ $# -ge 2 ]] &#124;&#124; { echo "--target requires map or pbap." >&2; exit 2; } | OBEX-SESSION: success, rejection, unavailable/malformed and cleanup as applicable |
| 40 | --help&#124;-h) | OBEX-SESSION: success, rejection, unavailable/malformed and cleanup as applicable |
| 44 | *) | OBEX-SESSION: success, rejection, unavailable/malformed and cleanup as applicable |
| 52 | if [[ ! "$DEVICE" =~ ^([[:xdigit:]]{2}:){5}[[:xdigit:]]{2}$ ]]; then | OBEX-SESSION: success, rejection, unavailable/malformed and cleanup as applicable |
| 57 | if [[ ! "$CONNECT_TIMEOUT" =~ ^[1-9][0-9]*$ ]]; then | OBEX-SESSION: success, rejection, unavailable/malformed and cleanup as applicable |
| 62 | case "$TARGET" in | OBEX-SESSION: success, rejection, unavailable/malformed and cleanup as applicable |
| 63 | map) | OBEX-SESSION: success, rejection, unavailable/malformed and cleanup as applicable |
| 68 | pbap) | OBEX-SESSION: success, rejection, unavailable/malformed and cleanup as applicable |
| 73 | *) | OBEX-SESSION: success, rejection, unavailable/malformed and cleanup as applicable |
| 79 | for command in busctl bluetoothctl obexctl stdbuf mktemp; do | OBEX-SESSION: success, rejection, unavailable/malformed and cleanup as applicable |
| 80 | if ! command -v "$command" >/dev/null 2>&1; then | OBEX-SESSION: success, rejection, unavailable/malformed and cleanup as applicable |
| 89 | if ! busctl --user list 2>/dev/null &#124; awk '{print $1}' &#124; grep -Fxq org.bluez.obex; then | OBEX-SESSION: success, rejection, unavailable/malformed and cleanup as applicable |
| 96 | if ! bluetoothctl info "$DEVICE" 2>/dev/null &#124; grep -Eq '^[[:space:]]*Paired:[[:space:]]+yes$'; then | OBEX-SESSION: success, rejection, unavailable/malformed and cleanup as applicable |
| 112 | cleanup() { | OBEX-SESSION: success, rejection, unavailable/malformed and cleanup as applicable |
| 115 | if [[ -n "$OBEX_FD" ]]; then | OBEX-SESSION: success, rejection, unavailable/malformed and cleanup as applicable |
| 116 | printf 'disconnect\nquit\n' >&"$OBEX_FD" 2>/dev/null &#124;&#124; true | OBEX-SESSION: success, rejection, unavailable/malformed and cleanup as applicable |
| 117 | exec {OBEX_FD}>&- 2>/dev/null &#124;&#124; true | OBEX-SESSION: success, rejection, unavailable/malformed and cleanup as applicable |
| 120 | if [[ -n "$OBEX_PID" ]] && kill -0 "$OBEX_PID" 2>/dev/null; then | OBEX-SESSION: success, rejection, unavailable/malformed and cleanup as applicable |
| 121 | for _ in 1 2 3 4 5; do | OBEX-SESSION: success, rejection, unavailable/malformed and cleanup as applicable |
| 122 | kill -0 "$OBEX_PID" 2>/dev/null &#124;&#124; break | OBEX-SESSION: success, rejection, unavailable/malformed and cleanup as applicable |
| 125 | kill "$OBEX_PID" 2>/dev/null &#124;&#124; true | OBEX-SESSION: success, rejection, unavailable/malformed and cleanup as applicable |
| 126 | wait "$OBEX_PID" 2>/dev/null &#124;&#124; true | OBEX-SESSION: success, rejection, unavailable/malformed and cleanup as applicable |
| 139 | wait_for_log() { | OBEX-SESSION: success, rejection, unavailable/malformed and cleanup as applicable |
| 144 | while (( elapsed < timeout_seconds * 10 )); do | OBEX-SESSION: success, rejection, unavailable/malformed and cleanup as applicable |
| 145 | if grep -Eq "$pattern" "$OBEX_LOG" 2>/dev/null; then | OBEX-SESSION: success, rejection, unavailable/malformed and cleanup as applicable |
| 148 | if ! kill -0 "$OBEX_PID" 2>/dev/null; then | OBEX-SESSION: success, rejection, unavailable/malformed and cleanup as applicable |
| 152 | ((elapsed += 1)) | OBEX-SESSION: success, rejection, unavailable/malformed and cleanup as applicable |
| 158 | if ! wait_for_log 'Client .*/org/bluez/obex&#124;\[NEW\].*Client' 5; then | OBEX-SESSION: success, rejection, unavailable/malformed and cleanup as applicable |
| 167 | if ! wait_for_log 'Connection successful&#124;Failed to connect' "$CONNECT_TIMEOUT"; then | OBEX-SESSION: success, rejection, unavailable/malformed and cleanup as applicable |
| 173 | if grep -Fq 'Failed to connect' "$OBEX_LOG"; then | OBEX-SESSION: success, rejection, unavailable/malformed and cleanup as applicable |
| 175 | failure="$(grep -F 'Failed to connect' "$OBEX_LOG" &#124; tail -n 1 &#124; sed -E 's/[[:space:]]+/ /g' &#124; cut -c1-220)" | OBEX-SESSION: success, rejection, unavailable/malformed and cleanup as applicable |
| 185 | if [[ -z "$SESSION_PATH" ]]; then | OBEX-SESSION: success, rejection, unavailable/malformed and cleanup as applicable |
| 193 | if busctl --user introspect   org.bluez.obex   "$SESSION_PATH"   org.bluez.obex.Session1 >/dev/null 2>&1; then | OBEX-SESSION: success, rejection, unavailable/malformed and cleanup as applicable |
| 207 | if [[ $TARGET_STATUS -eq 0 ]]; then | OBEX-SESSION: success, rejection, unavailable/malformed and cleanup as applicable |
| 213 | if [[ "$SESSION_TARGET_UUID" == "$EXPECTED_TARGET_UUID" ]]; then | OBEX-SESSION: success, rejection, unavailable/malformed and cleanup as applicable |
| 223 | if busctl --user introspect   org.bluez.obex   "$SESSION_PATH"   "$EXPECTED_INTERFACE" >/dev/null 2>&1; then | OBEX-SESSION: success, rejection, unavailable/malformed and cleanup as applicable |
| 229 | if wait_for_log "\[NEW\].*$EXPECTED_PROXY_LABEL&#124;$EXPECTED_PROXY_LABEL /org/bluez/obex/client/session" 2; then | OBEX-SESSION: success, rejection, unavailable/malformed and cleanup as applicable |
| 235 | if busctl --user introspect   org.bluez.obex   "$SESSION_PATH"   "$EXPECTED_INTERFACE" >/dev/null 2>&1; then | OBEX-SESSION: success, rejection, unavailable/malformed and cleanup as applicable |

## scripts/verify-deb.sh

| Source line | Decision / method | Planned assertion family |
| --- | --- | --- |
| 4 | if [[ $# -ne 1 ]]; then | VERIFY-DEB: success, rejection, unavailable/malformed and cleanup as applicable |
| 10 | if [[ ! -f "$PACKAGE_PATH" ]]; then | VERIFY-DEB: success, rejection, unavailable/malformed and cleanup as applicable |
| 15 | for command in dpkg-deb sha256sum; do | VERIFY-DEB: success, rejection, unavailable/malformed and cleanup as applicable |
| 16 | if ! command -v "$command" >/dev/null 2>&1; then | VERIFY-DEB: success, rejection, unavailable/malformed and cleanup as applicable |
| 23 | if [[ ! -f "$SIDE_CAR" ]]; then | VERIFY-DEB: success, rejection, unavailable/malformed and cleanup as applicable |
| 33 | assert_field() { | VERIFY-DEB: success, rejection, unavailable/malformed and cleanup as applicable |
| 39 | if [[ "$actual" != "$expected" ]]; then | VERIFY-DEB: success, rejection, unavailable/malformed and cleanup as applicable |
| 48 | if [[ ! "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+([.-][0-9A-Za-z.-]+)?$ ]]; then | VERIFY-DEB: success, rejection, unavailable/malformed and cleanup as applicable |
| 54 | case "$architecture" in | VERIFY-DEB: success, rejection, unavailable/malformed and cleanup as applicable |
| 55 | amd64&#124;arm64) | VERIFY-DEB: success, rejection, unavailable/malformed and cleanup as applicable |
| 57 | *) | VERIFY-DEB: success, rejection, unavailable/malformed and cleanup as applicable |
| 64 | dependency_present() { | VERIFY-DEB: success, rejection, unavailable/malformed and cleanup as applicable |
| 68 | sed 's/^[[:space:]]*//' &#124; | VERIFY-DEB: success, rejection, unavailable/malformed and cleanup as applicable |
| 69 | grep -Eq "^$dependency([[:space:](]&#124;$)" | VERIFY-DEB: success, rejection, unavailable/malformed and cleanup as applicable |
| 72 | for dependency in bluez bluez-obexd; do | VERIFY-DEB: success, rejection, unavailable/malformed and cleanup as applicable |
| 73 | if ! dependency_present "$dependency"; then | VERIFY-DEB: success, rejection, unavailable/malformed and cleanup as applicable |
| 84 | test -x "$TEMP_DIR/usr/bin/nativepair" | VERIFY-DEB: success, rejection, unavailable/malformed and cleanup as applicable |
| 85 | test -x "$TEMP_DIR/usr/libexec/nativepair-daemon" | VERIFY-DEB: success, rejection, unavailable/malformed and cleanup as applicable |
| 86 | test -f "$TEMP_DIR/usr/share/doc/nativepair/LICENSE" | VERIFY-DEB: success, rejection, unavailable/malformed and cleanup as applicable |
| 87 | test -f "$TEMP_DIR/usr/share/doc/nativepair/NOTICE" | VERIFY-DEB: success, rejection, unavailable/malformed and cleanup as applicable |
| 88 | test -f "$TEMP_DIR/usr/share/doc/nativepair/README.md" | VERIFY-DEB: success, rejection, unavailable/malformed and cleanup as applicable |

## scripts/probe_call_audio_watch.py

| Source line | Decision / method | Planned assertion family |
| --- | --- | --- |
| 16 | def command(args): | WATCH: both outcomes, boundary variants and malformed data |
| 21 | except (OSError, subprocess.TimeoutExpired): | WATCH: both outcomes, boundary variants and malformed data |
| 23 | return result.stdout if result.returncode == 0 else None | WATCH: both outcomes, boundary variants and malformed data |
| 26 | def parse_wpctl_id(output): | WATCH: both outcomes, boundary variants and malformed data |
| 28 | return int(match.group(1)) if match else None | WATCH: both outcomes, boundary variants and malformed data |
| 31 | def parse_sink_mute(output): | WATCH: both outcomes, boundary variants and malformed data |
| 32 | if output is None or not output.startswith("Volume:"): | WATCH: both outcomes, boundary variants and malformed data |
| 34 | return "yes" if "[MUTED]" in output else "no" | WATCH: both outcomes, boundary variants and malformed data |
| 37 | def is_bluetooth(props): | WATCH: both outcomes, boundary variants and malformed data |
| 43 | def graph_snapshot(objects, sink_id, source_id, sink_muted, call_present): | WATCH: both outcomes, boundary variants and malformed data |
| 47 | for obj in objects: | WATCH: both outcomes, boundary variants and malformed data |
| 49 | if obj.get("type") == "PipeWire:Interface:Node": | WATCH: both outcomes, boundary variants and malformed data |
| 51 | elif obj.get("type") == "PipeWire:Interface:Link": | WATCH: both outcomes, boundary variants and malformed data |
| 54 | def props(nid): | WATCH: both outcomes, boundary variants and malformed data |
| 70 | if sink_state not in ("running", "idle", "suspended", "error"): | WATCH: both outcomes, boundary variants and malformed data |
| 74 | "default_sink_present": "yes" if sink_id is not None else "no", | WATCH: both outcomes, boundary variants and malformed data |
| 75 | "default_sink_is_bluetooth": "yes" if is_bluetooth(props(sink_id)) else "no", | WATCH: both outcomes, boundary variants and malformed data |
| 78 | "default_source_present": "yes" if source_id is not None else "no", | WATCH: both outcomes, boundary variants and malformed data |
| 79 | "default_source_is_bluetooth": "yes" if is_bluetooth(props(source_id)) else "no", | WATCH: both outcomes, boundary variants and malformed data |
| 91 | def find_gateway(): | WATCH: both outcomes, boundary variants and malformed data |
| 95 | return gateways[0] if len(gateways) == 1 else None | WATCH: both outcomes, boundary variants and malformed data |
| 98 | def call_present(gateway): | WATCH: both outcomes, boundary variants and malformed data |
| 99 | if gateway is None: | WATCH: both outcomes, boundary variants and malformed data |
| 103 | if output is None: | WATCH: both outcomes, boundary variants and malformed data |
| 105 | return "yes" if CALL_PATH.search(output) else "no" | WATCH: both outcomes, boundary variants and malformed data |
| 108 | def sample(gateway): | WATCH: both outcomes, boundary variants and malformed data |
| 110 | if raw is None: | WATCH: both outcomes, boundary variants and malformed data |
| 114 | except json.JSONDecodeError: | WATCH: both outcomes, boundary variants and malformed data |
| 116 | if not isinstance(objects, list): | WATCH: both outcomes, boundary variants and malformed data |
| 124 | def emit(index, elapsed, state, first_sink, sink, first_source, source): | WATCH: both outcomes, boundary variants and malformed data |
| 127 | print("default_sink_changed=" + ("yes" if sink != first_sink else "no"), flush=True) | WATCH: both outcomes, boundary variants and malformed data |
| 128 | print("default_source_changed=" + ("yes" if source != first_source else "no"), flush=True) | WATCH: both outcomes, boundary variants and malformed data |
| 129 | for name, value in state.items(): | WATCH: both outcomes, boundary variants and malformed data |
| 134 | def main(): | WATCH: both outcomes, boundary variants and malformed data |
| 139 | if not (5 <= args.seconds <= 90) or not (250 <= args.interval_ms <= 2000): | WATCH: both outcomes, boundary variants and malformed data |
| 141 | if not all(shutil.which(cmd) for cmd in ("pw-dump", "wpctl", "busctl")): | WATCH: both outcomes, boundary variants and malformed data |
| 151 | print("telephony_gateway_resolved=" + ("yes" if gateway else "no")) | WATCH: both outcomes, boundary variants and malformed data |
| 158 | while time.monotonic() - start < args.seconds: | WATCH: both outcomes, boundary variants and malformed data |
| 160 | if result is None: | WATCH: both outcomes, boundary variants and malformed data |
| 164 | if count == 0: | WATCH: both outcomes, boundary variants and malformed data |
| 175 | if comparison != previous: | WATCH: both outcomes, boundary variants and malformed data |
| 181 | except KeyboardInterrupt: | WATCH: both outcomes, boundary variants and malformed data |
| 187 | print("call_observed=" + ("yes" if call_seen else "no")) | WATCH: both outcomes, boundary variants and malformed data |
| 188 | print("sink_muted_at_any_time=" + ("yes" if mute_seen else "no")) | WATCH: both outcomes, boundary variants and malformed data |
| 189 | print("default_sink_changed_at_any_time=" + ("yes" if sink_changed else "no")) | WATCH: both outcomes, boundary variants and malformed data |
| 190 | print("hfp_nodes_observed=" + ("yes" if hfp_seen else "no")) | WATCH: both outcomes, boundary variants and malformed data |
| 192 | ("yes" if stream_disruption else "no")) | WATCH: both outcomes, boundary variants and malformed data |
| 193 | print("probe_complete=" + ("yes" if count else "no")) | WATCH: both outcomes, boundary variants and malformed data |
| 195 | return 0 if count else 1 | WATCH: both outcomes, boundary variants and malformed data |
| 198 | if __name__ == "__main__": | WATCH: both outcomes, boundary variants and malformed data |

## crates/nativepair-cli/src/main.rs

| Source line | Decision / method | Planned assertion family |
| --- | --- | --- |
| 18 | fn main() -> ExitCode { | CLI/DAEMON: argv and exit-code matrix |
| 21 | match args.next().as_deref() { | CLI/DAEMON: argv and exit-code matrix |
| 22 | Some("--version" &#124; "-V") if args.next().is_none() => { | CLI/DAEMON: argv and exit-code matrix |
| 26 | Some("--help" &#124; "-h") if args.next().is_none() => { | CLI/DAEMON: argv and exit-code matrix |

## crates/nativepair-core/src/lib.rs

| Source line | Decision / method | Planned assertion family |
| --- | --- | --- |
| 53 | pub fn new(platform: PhonePlatform) -> Self { | CORE: exhaustive state matrix |
| 61 | pub const fn platform(&self) -> PhonePlatform { | CORE: exhaustive state matrix |
| 66 | pub fn availability(&self, capability: Capability) -> Availability { | CORE: exhaustive state matrix |
| 73 | pub fn set_availability( | CORE: exhaustive state matrix |
| 84 | pub fn supports(&self, capability: Capability) -> bool { | CORE: exhaustive state matrix |

## crates/nativepair-daemon/src/main.rs

| Source line | Decision / method | Planned assertion family |
| --- | --- | --- |
| 9 | fn main() -> ExitCode { | CLI/DAEMON: argv and exit-code matrix |
| 12 | match args.next().as_deref() { | CLI/DAEMON: argv and exit-code matrix |
| 13 | Some("--version" &#124; "-V") if args.next().is_none() => { | CLI/DAEMON: argv and exit-code matrix |
