# M1 current source branch map

Date: 2026-10-09. Status: HFP gateway classification and failed-node-wait observations implemented; complete 1665-method Python suite passed; process-stability verification pending.

This source decision index links methods, conditions, loops, command substitutions,
returns and cleanup exits to executable assertion families. It is an audit index,
not a denominator for instrumented branch coverage. Python scenario IDs are in
[the canonical inventory](evidence/m1-automated-test-inventory.json); exact inputs
and assertions are in linked tests. The original pre-implementation map is
preserved in Git commit a3718b3.

See [the functional coverage map](M1_COVERAGE_MAP.md) and
[GetCalls correction](M1_GETCALLS_COMPATIBILITY.md) for contracts and evidence.

## scripts/build-deb.sh

Assertion families: [test_packaging_contract](../scripts/tests/test_packaging_contract.py), [test_packaging_branches](../scripts/tests/test_packaging_branches.py).

| Source line | Decision / method | Assertion mapping |
| --- | --- | --- |
| 3 | trap 'exit 130' INT | test_packaging_contract, test_packaging_branches |
| 4 | trap 'exit 143' TERM | test_packaging_contract, test_packaging_branches |
| 6 | ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)" | test_packaging_contract, test_packaging_branches |
| 9 | for command in cargo dpkg dpkg-deb python3 sha256sum; do | test_packaging_contract, test_packaging_branches |
| 10 | if ! command -v "$command" >/dev/null 2>&1; then | test_packaging_contract, test_packaging_branches |
| 12 | exit 1 | test_packaging_contract, test_packaging_branches |
| 17 | if [[ -z "$VERSION" ]]; then | test_packaging_contract, test_packaging_branches |
| 18 | VERSION="$( | test_packaging_contract, test_packaging_branches |
| 20 | python3 -c 'import json, sys; data = json.load(sys.stdin); print(next(p["version"] for p in data["packages"] if p["name"] == "nativepair-core"))' | test_packaging_contract, test_packaging_branches |
| 24 | if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+([.-][0-9A-Za-z.-]+)?$ ]]; then | test_packaging_contract, test_packaging_branches |
| 26 | exit 1 | test_packaging_contract, test_packaging_branches |
| 29 | HOST_ARCH="$(dpkg --print-architecture)" | test_packaging_contract, test_packaging_branches |
| 31 | case "$ARCH" in | test_packaging_contract, test_packaging_branches |
| 36 | exit 1 | test_packaging_contract, test_packaging_branches |
| 39 | if [[ "$ARCH" != "$HOST_ARCH" ]]; then | test_packaging_contract, test_packaging_branches |
| 41 | exit 1 | test_packaging_contract, test_packaging_branches |
| 64 | installed_size="$(du -sk "$PACKAGE_ROOT/usr" \| awk '{print $1}')" | test_packaging_contract, test_packaging_branches |
| 67 | if [[ -z "${SOURCE_DATE_EPOCH:-}" ]] && command -v git >/dev/null 2>&1; then | test_packaging_contract, test_packaging_branches |
| 68 | SOURCE_DATE_EPOCH="$(git log -1 --format=%ct 2>/dev/null \|\| true)" | test_packaging_contract, test_packaging_branches |
| 70 | if [[ -n "${SOURCE_DATE_EPOCH:-}" ]]; then | test_packaging_contract, test_packaging_branches |
| 72 | while IFS= read -r -d '' path; do | test_packaging_contract, test_packaging_branches |

## scripts/verify-deb.sh

Assertion families: [test_packaging_contract](../scripts/tests/test_packaging_contract.py), [test_packaging_branches](../scripts/tests/test_packaging_branches.py).

| Source line | Decision / method | Assertion mapping |
| --- | --- | --- |
| 3 | trap 'exit 130' INT | test_packaging_contract, test_packaging_branches |
| 4 | trap 'exit 143' TERM | test_packaging_contract, test_packaging_branches |
| 6 | if [[ $# -ne 1 ]]; then | test_packaging_contract, test_packaging_branches |
| 8 | exit 2 | test_packaging_contract, test_packaging_branches |
| 11 | PACKAGE_PATH="$(readlink -f "$1")" | test_packaging_contract, test_packaging_branches |
| 12 | if [[ ! -f "$PACKAGE_PATH" ]]; then | test_packaging_contract, test_packaging_branches |
| 14 | exit 1 | test_packaging_contract, test_packaging_branches |
| 17 | for command in dpkg-deb sha256sum awk; do | test_packaging_contract, test_packaging_branches |
| 18 | if ! command -v "$command" >/dev/null 2>&1; then | test_packaging_contract, test_packaging_branches |
| 20 | exit 1 | test_packaging_contract, test_packaging_branches |
| 25 | if [[ ! -f "$SIDE_CAR" ]]; then | test_packaging_contract, test_packaging_branches |
| 27 | exit 1 | test_packaging_contract, test_packaging_branches |
| 30 | if ! awk -v name="$(basename "$PACKAGE_PATH")" ' | test_packaging_contract, test_packaging_branches |
| 31 | NR == 1 { valid = length($1) == 64 && $1 ~ /^[[:xdigit:]]+$/ && NF == 2 && ($2 == name \|\| $2 == "*" name) } | test_packaging_contract, test_packaging_branches |
| 32 | END { exit !(NR == 1 && valid) } | test_packaging_contract, test_packaging_branches |
| 34 | echo "Invalid checksum sidecar: expected one checksum for this package." >&2 | test_packaging_contract, test_packaging_branches |
| 35 | exit 1 | test_packaging_contract, test_packaging_branches |
| 39 | cd "$(dirname "$PACKAGE_PATH")" | test_packaging_contract, test_packaging_branches |
| 40 | sha256sum --check "$(basename "$SIDE_CAR")" | test_packaging_contract, test_packaging_branches |
| 43 | assert_field() { | test_packaging_contract, test_packaging_branches |
| 48 | actual="$(dpkg-deb --field "$PACKAGE_PATH" "$field")" | test_packaging_contract, test_packaging_branches |
| 49 | if [[ "$actual" != "$expected" ]]; then | test_packaging_contract, test_packaging_branches |
| 51 | exit 1 | test_packaging_contract, test_packaging_branches |
| 57 | version="$(dpkg-deb --field "$PACKAGE_PATH" Version)" | test_packaging_contract, test_packaging_branches |
| 58 | if [[ ! "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+([.-][0-9A-Za-z.-]+)?$ ]]; then | test_packaging_contract, test_packaging_branches |
| 60 | exit 1 | test_packaging_contract, test_packaging_branches |
| 63 | architecture="$(dpkg-deb --field "$PACKAGE_PATH" Architecture)" | test_packaging_contract, test_packaging_branches |
| 64 | case "$architecture" in | test_packaging_contract, test_packaging_branches |
| 69 | exit 1 | test_packaging_contract, test_packaging_branches |
| 73 | depends="$(dpkg-deb --field "$PACKAGE_PATH" Depends)" | test_packaging_contract, test_packaging_branches |
| 74 | dependency_present() { | test_packaging_contract, test_packaging_branches |
| 82 | for dependency in bluez bluez-obexd; do | test_packaging_contract, test_packaging_branches |
| 83 | if ! dependency_present "$dependency"; then | test_packaging_contract, test_packaging_branches |
| 85 | exit 1 | test_packaging_contract, test_packaging_branches |
| 89 | TEMP_DIR="$(mktemp -d)" | test_packaging_contract, test_packaging_branches |
| 90 | trap 'rm -rf "$TEMP_DIR"' EXIT | test_packaging_contract, test_packaging_branches |
| 103 | echo "Debian package verification passed: $(basename "$PACKAGE_PATH")" | test_packaging_contract, test_packaging_branches |

## scripts/probe-audio-health.sh

Assertion families: [test_audio_diagnostics_contract](../scripts/tests/test_audio_diagnostics_contract.py), [test_probe_parameters](../scripts/tests/test_probe_parameters.py), [test_remaining_contracts](../scripts/tests/test_remaining_contracts.py), [test_hfp_node_classification](../scripts/tests/test_hfp_node_classification.py).

| Source line | Decision / method | Assertion mapping |
| --- | --- | --- |
| 8 | if [[ ! "$ITERATIONS" =~ ^0*([2-9]\|[1-5][0-9]\|60)$ ]]; then | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 10 | exit 2 | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 13 | ITERATIONS=$((10#$ITERATIONS)) | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 15 | for command in grep journalctl mktemp pw-dump python3 pw-top sed systemctl timeout wpctl; do | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 16 | if ! command -v "$command" >/dev/null 2>&1; then | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 18 | exit 1 | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 22 | TMP_DIR="$(mktemp -d)" | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 31 | cleanup() { | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 34 | trap cleanup EXIT | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 35 | trap 'exit 130' INT | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 36 | trap 'exit 143' TERM | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 43 | if systemctl --user is-active --quiet pipewire.service 2>/dev/null; then | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 45 | else | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 49 | if systemctl --user is-active --quiet wireplumber.service 2>/dev/null; then | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 51 | else | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 55 | if ! pw-dump >"$PW_DUMP" 2>/dev/null; then | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 57 | exit 1 | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 64 | if wpctl inspect @DEFAULT_AUDIO_SINK@ >"$DEFAULT_SINK_REPLY" 2>/dev/null; then | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 65 | DEFAULT_SINK_ID="$(sed -nE 's/^id ([0-9]+),.*/\1/p' "$DEFAULT_SINK_REPLY" \| head -n 1)" | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 68 | if wpctl inspect @DEFAULT_AUDIO_SOURCE@ >"$DEFAULT_SOURCE_REPLY" 2>/dev/null; then | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 69 | DEFAULT_SOURCE_ID="$(sed -nE 's/^id ([0-9]+),.*/\1/p' "$DEFAULT_SOURCE_REPLY" \| head -n 1)" | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 73 | timeout "$((ITERATIONS + 8))s" pw-top -b -n "$ITERATIONS" >"$PW_TOP_RAW" 2>/dev/null | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 77 | if [[ $PW_TOP_STATUS -ne 0 ]]; then | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 80 | exit 1 | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 84 | python3 - "$PW_TOP_RAW" "$PW_DUMP" "$DEFAULT_SINK_ID" "$DEFAULT_SOURCE_ID" "$(dirname -- "${BASH_SOURCE[0]}")" >"$PW_TOP_RESULT" <<'PY' \|\| { cat "$PW_TOP_RESULT"; exit 1; } | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 104 | for raw in handle: | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 106 | if not line: | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 108 | if line.startswith("S   ID  QUANT"): | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 113 | if len(parts) < 9: | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 122 | if state not in {"E", "C", "S", "I", "R", "t", "T", "!"}: | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 124 | if not node_id.isdigit() or not err.isdigit(): | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 128 | if state in {"R", "t", "T"}: | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 130 | if state == "E": | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 141 | if quant.isdigit() and rate.isdigit(): | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 144 | if q > 0 and r > 0: | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 149 | for nid in seen_ids | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 150 | if max_err.get(nid, 0) - first_err.get(nid, 0) > 0 | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 157 | sys.exit(1) | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 160 | for obj in dump: | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 165 | def props_for(nid): | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 166 | return props_by_id.get(str(nid), {}) | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 168 | def is_bluetooth(props): | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 169 | return ( | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 175 | def media_class(props): | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 176 | return str(props.get("media.class") or "") | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 178 | def default_kind(node_id): | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 179 | if not node_id: | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 180 | return "unknown" | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 182 | if props is None: | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 183 | return "unknown" | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 184 | return "yes" if is_bluetooth(props) else "no" | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 188 | for nid, delta in growth.items() | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 189 | if states_seen.get(nid, set()) & {"R", "t", "T"} | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 192 | nid: delta for nid, delta in growth.items() if is_bluetooth(props_for(nid)) | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 195 | nid: delta for nid, delta in growth.items() if is_hfp(props_for(nid)) | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 199 | for nid, delta in growth.items() | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 200 | if media_class(props_for(nid)).startswith("Stream/Output/Audio") | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 204 | for nid, delta in growth.items() | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 205 | if media_class(props_for(nid)) == "Audio/Sink" | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 209 | for nid, delta in growth.items() | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 210 | if media_class(props_for(nid)) == "Audio/Source" | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 220 | default_sink_delta = growth.get(int(default_sink_id), 0) if default_sink_id.isdigit() else 0 | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 221 | default_source_delta = growth.get(int(default_source_id), 0) if default_source_id.isdigit() else 0 | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 223 | positive_now = sum(1 for value in last_err.values() if value > 0) | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 236 | print(f"xrun_or_error_growth_observed={'yes' if growth else 'no'}") | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 239 | print(f"default_sink_snapshot_available={'yes' if default_sink_id else 'no'}") | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 240 | print(f"default_source_snapshot_available={'yes' if default_source_id else 'no'}") | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 243 | print(f"default_sink_err_growth={'yes' if default_sink_delta > 0 else 'no'}") | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 245 | print(f"default_source_err_growth={'yes' if default_source_delta > 0 else 'no'}") | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 254 | print(f"bluetooth_err_growth_observed={'yes' if bluetooth_growth else 'no'}") | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 255 | print(f"hfp_err_growth_observed={'yes' if hfp_growth else 'no'}") | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 256 | print(f"output_stream_err_growth_observed={'yes' if output_stream_growth else 'no'}") | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 261 | journalctl --user -u pipewire.service --since "-$RECENT_WINDOW" -p warning   --no-pager --output=cat >"$PIPEWIRE_LOG" 2>/dev/null \|\| true | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 262 | journalctl --user -u wireplumber.service --since "-$RECENT_WINDOW" -p warning   --no-pager --output=cat >"$WIREPLUMBER_LOG" 2>/dev/null \|\| true | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 264 | PIPEWIRE_WARNINGS="$(grep -cve '^[[:space:]]*$' "$PIPEWIRE_LOG" \|\| true)" | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 265 | WIREPLUMBER_WARNINGS="$(grep -cve '^[[:space:]]*$' "$WIREPLUMBER_LOG" \|\| true)" | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 270 | if grep -Eqi 'xrun\|underrun\|overrun\|deadline\|missed' "$PIPEWIRE_LOG" "$WIREPLUMBER_LOG"; then | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 272 | else | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 276 | if grep -Eqi 'bluez\|bluetooth\|sco\|hfp\|transport' "$PIPEWIRE_LOG" "$WIREPLUMBER_LOG"; then | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 278 | else | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |

## scripts/probe-audio-routing.sh

Assertion families: [test_audio_diagnostics_contract](../scripts/tests/test_audio_diagnostics_contract.py), [test_probe_parameters](../scripts/tests/test_probe_parameters.py), [test_remaining_contracts](../scripts/tests/test_remaining_contracts.py), [test_hfp_node_classification](../scripts/tests/test_hfp_node_classification.py).

| Source line | Decision / method | Assertion mapping |
| --- | --- | --- |
| 10 | if [[ ! "$DEVICE" =~ ^([[:xdigit:]]{2}:){5}[[:xdigit:]]{2}$ ]]; then | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 12 | exit 2 | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 15 | for command in awk busctl grep head mktemp python3 pw-dump sed wpctl; do | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 16 | if ! command -v "$command" >/dev/null 2>&1; then | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 18 | exit 1 | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 22 | TMP_DIR="$(mktemp -d)" | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 30 | cleanup() { | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 33 | trap cleanup EXIT | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 34 | trap 'exit 130' INT | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 35 | trap 'exit 143' TERM | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 42 | if busctl --user call "$TELEPHONY_SERVICE" "$TELEPHONY_MANAGER"   org.ofono.Manager GetModems >"$MODEMS_REPLY" 2>/dev/null; then | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 43 | AG_PATH="$(awk -F'"' ' | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 44 | { for (i = 2; i <= NF; i += 2) if ($i ~ /^\/org\/pipewire\/Telephony\/ag[0-9]+$/) seen[$i] = 1 } | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 45 | END { for (path in seen) { count++; last = path } if (count == 1) print last } | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 49 | if [[ -n "$AG_PATH" ]]; then | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 51 | if busctl --user get-property "$TELEPHONY_SERVICE" "$AG_PATH"     "$TRANSPORT_IFACE" State >"$STATE_REPLY" 2>/dev/null; then | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 52 | STATE="$(sed -nE 's/^s "(idle\|pending\|active\|error)"$/\1/p' "$STATE_REPLY")" | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 54 | else | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 57 | else | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 62 | if ! pw-dump >"$PW_DUMP" 2>/dev/null; then | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 64 | exit 1 | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 71 | if wpctl inspect @DEFAULT_AUDIO_SINK@ >"$DEFAULT_SINK_REPLY" 2>/dev/null; then | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 72 | DEFAULT_SINK_ID="$(sed -nE 's/^id ([0-9]+),.*/\1/p' "$DEFAULT_SINK_REPLY" \| head -n 1)" | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 75 | if wpctl inspect @DEFAULT_AUDIO_SOURCE@ >"$DEFAULT_SOURCE_REPLY" 2>/dev/null; then | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 76 | DEFAULT_SOURCE_ID="$(sed -nE 's/^id ([0-9]+),.*/\1/p' "$DEFAULT_SOURCE_REPLY" \| head -n 1)" | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 79 | python3 - "$PW_DUMP" "$DEVICE" "$DEFAULT_SINK_ID" "$DEFAULT_SOURCE_ID" "$(dirname -- "${BASH_SOURCE[0]}")" >"$ROUTING_RESULT" <<'PY' \|\| { cat "$ROUTING_RESULT"; exit 1; } | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 90 | sys.exit(1) | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 93 | for obj in data: | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 96 | if props.get("api.bluez5.address") != device: | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 98 | if not is_hfp(props): | test_hfp_node_classification |
| 102 | source_ids = {node_id for node_id, props in hfp_nodes if props.get("media.class") == "Audio/Source"} | test_hfp_node_classification |
| 103 | sink_ids = {node_id for node_id, props in hfp_nodes if props.get("media.class") == "Audio/Sink"} | test_hfp_node_classification |
| 108 | print(f"hfp_source_node_present={'yes' if source_present else 'no'}") | test_hfp_node_classification |
| 109 | print(f"hfp_sink_node_present={'yes' if sink_present else 'no'}") | test_hfp_node_classification |
| 110 | print(f"default_sink_snapshot_available={'yes' if default_sink_id else 'no'}") | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 111 | print(f"default_source_snapshot_available={'yes' if default_source_id else 'no'}") | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 112 | print(f"default_sink_is_phone_hfp={'yes' if default_sink_id in sink_ids else 'no'}") | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 113 | print(f"default_source_is_phone_hfp={'yes' if default_source_id in source_ids else 'no'}") | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |
| 114 | print(f"orphan_hfp_nodes_present={'yes' if hfp_nodes else 'no'}") | test_audio_diagnostics_contract, test_probe_parameters, test_remaining_contracts |

## scripts/probe-bluetooth.sh

Assertion families: [test_discovery_contract](../scripts/tests/test_discovery_contract.py), [test_probe_parameters](../scripts/tests/test_probe_parameters.py), [test_remaining_contracts](../scripts/tests/test_remaining_contracts.py).

| Source line | Decision / method | Assertion mapping |
| --- | --- | --- |
| 8 | usage() { | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 25 | while [[ $# -gt 0 ]]; do | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 26 | case "$1" in | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 28 | if [[ $# -lt 2 ]]; then | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 30 | exit 2 | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 42 | exit 0 | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 47 | exit 2 | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 52 | if [[ -n "$DEVICE" ]] && [[ ! "$DEVICE" =~ ^([[:xdigit:]]{2}:){5}[[:xdigit:]]{2}$ ]]; then | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 54 | exit 2 | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 57 | command_present() { | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 58 | if command -v "$1" >/dev/null 2>&1; then | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 60 | else | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 65 | bool_line() { | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 70 | echo "probe_scope=host$([[ -n "$DEVICE" ]] && printf '+device')" | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 72 | bool_line bluetoothctl_present "$(command_present bluetoothctl)" | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 73 | bool_line busctl_present "$(command_present busctl)" | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 74 | bool_line obexctl_present "$(command_present obexctl)" | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 76 | if command -v bluetoothctl >/dev/null 2>&1; then | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 77 | version="$(bluetoothctl --version 2>/dev/null \| head -n 1 \| tr -cd '[:alnum:].:_ -')" | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 80 | adapter_count="$( | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 86 | paired_count="$( | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 88 | bluetoothctl devices Paired 2>/dev/null \|\| | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 89 | bluetoothctl paired-devices 2>/dev/null \|\| | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 95 | else | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 101 | if command -v systemctl >/dev/null 2>&1 && | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 104 | else | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 108 | if command -v busctl >/dev/null 2>&1 && | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 111 | else | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 115 | if command -v systemctl >/dev/null 2>&1 && | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 118 | else | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 122 | if [[ "$HOST_ONLY" == yes \|\| -z "$DEVICE" ]]; then | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 123 | exit 0 | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 126 | if ! command -v bluetoothctl >/dev/null 2>&1; then | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 128 | exit 1 | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 131 | info="$(bluetoothctl info "$DEVICE" 2>/dev/null \|\| true)" | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 132 | if [[ -z "$info" ]]; then | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 134 | exit 1 | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 139 | property_is_yes() { | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 141 | if grep -Eq "^[[:space:]]*$property:[[:space:]]+yes$" <<<"$info"; then | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 143 | else | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 148 | bool_line device_paired "$(property_is_yes Paired)" | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 149 | bool_line device_trusted "$(property_is_yes Trusted)" | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 150 | bool_line device_connected "$(property_is_yes Connected)" | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 152 | lower_info="$(tr '[:upper:]' '[:lower:]' <<<"$info")" | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 154 | uuid_present() { | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 156 | if grep -Fq "$uuid" <<<"$lower_info"; then | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 158 | else | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 163 | bool_line advertised_map_mse "$(uuid_present 00001132-0000-1000-8000-00805f9b34fb)" | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 164 | bool_line advertised_pbap_pse "$(uuid_present 0000112f-0000-1000-8000-00805f9b34fb)" | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 165 | bool_line advertised_hfp_ag "$(uuid_present 0000111f-0000-1000-8000-00805f9b34fb)" | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 166 | bool_line advertised_ancs "$(uuid_present 7905f431-b5ce-4e99-a40f-4b1e122d00d0)" | test_discovery_contract, test_probe_parameters, test_remaining_contracts |

## scripts/probe-call-audio-watch.sh

Assertion families: [test_watcher_entry](../scripts/tests/test_watcher_entry.py).

| Source line | Decision / method | Assertion mapping |
| --- | --- | --- |
| 3 | exec python3 "$(dirname -- "$0")/probe_call_audio_watch.py" "$@" | test_watcher_entry |

## scripts/probe-hfp.sh

Assertion families: [test_hfp_contract_extended](../scripts/tests/test_hfp_contract_extended.py), [test_probe_parameters](../scripts/tests/test_probe_parameters.py), [test_remaining_contracts](../scripts/tests/test_remaining_contracts.py), [test_getcalls_compatibility](../scripts/tests/test_getcalls_compatibility.py).

| Source line | Decision / method | Assertion mapping |
| --- | --- | --- |
| 11 | usage() { | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 25 | if [[ "${1:-}" == "--help" \|\| "${1:-}" == "-h" ]]; then | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 27 | exit 0 | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 30 | if [[ $# -ne 0 ]]; then | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 33 | exit 2 | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 36 | if [[ ! "$DEVICE" =~ ^([[:xdigit:]]{2}:){5}[[:xdigit:]]{2}$ ]]; then | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 38 | exit 2 | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 41 | if [[ ! "$CONNECT_TIMEOUT" =~ ^[1-9][0-9]{0,17}$ ]] \|\| (( CONNECT_TIMEOUT > 922337203685477580 )); then | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 43 | exit 2 | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 46 | for command in bluetoothctl busctl grep awk sed head tail tr mktemp timeout seq sleep; do | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 47 | if ! command -v "$command" >/dev/null 2>&1; then | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 49 | exit 1 | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 53 | TMP_DIR="$(mktemp -d)" | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 61 | cleanup() { | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 64 | trap cleanup EXIT | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 65 | trap 'exit 130' INT | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 66 | trap 'exit 143' TERM | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 68 | bool_line() { | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 77 | info="$(bluetoothctl info "$DEVICE" 2>/dev/null \|\| true)" | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 78 | if [[ -z "$info" ]]; then | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 80 | exit 1 | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 84 | if grep -Eq '^[[:space:]]*Paired:[[:space:]]+yes$' <<<"$info"; then | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 86 | else | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 88 | exit 1 | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 91 | if grep -Fqi "$HFP_AG_UUID" <<<"$info"; then | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 93 | else | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 95 | exit 1 | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 98 | if command -v systemctl >/dev/null 2>&1 && | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 101 | else | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 105 | if command -v systemctl >/dev/null 2>&1 && | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 108 | else | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 112 | if command -v pipewire >/dev/null 2>&1; then | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 113 | pipewire_version="$(pipewire --version 2>/dev/null \| tail -n 1 \| tr -cd '[:alnum:].:_ -')" | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 115 | else | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 119 | if command -v wireplumber >/dev/null 2>&1; then | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 120 | wireplumber_version="$(wireplumber --version 2>/dev/null \| tail -n 1 \| tr -cd '[:alnum:].:_ -')" | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 122 | else | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 126 | if busctl --user introspect "$TELEPHONY_SERVICE" "$TELEPHONY_MANAGER" >"$MANAGER_INTROSPECT" 2>/dev/null; then | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 128 | else | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 132 | if grep -Fq 'org.ofono.Manager' "$MANAGER_INTROSPECT" 2>/dev/null && | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 135 | else | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 148 | if [[ $CONNECT_STATUS -eq 124 ]]; then | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 150 | elif grep -Fq 'Connection successful' "$CONNECT_LOG"; then | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 152 | elif grep -Eqi 'already connected\|connected: yes' "$CONNECT_LOG"; then | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 154 | else | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 159 | for _ in $(seq 1 50); do | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 160 | if busctl --user call "$TELEPHONY_SERVICE" "$TELEPHONY_MANAGER"     org.ofono.Manager GetModems >"$MODEMS_REPLY" 2>/dev/null; then | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 161 | AG_PATH="$(awk -F'"' ' | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 162 | { for (i = 2; i <= NF; i += 2) if ($i ~ /^\/org\/pipewire\/Telephony\/ag[0-9]+$/) seen[$i] = 1 } | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 163 | END { for (path in seen) { count++; last = path } if (count == 1) print last } | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 165 | if [[ -n "$AG_PATH" ]]; then | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 172 | if [[ -n "$AG_PATH" ]]; then | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 175 | else | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 180 | if [[ -n "$AG_PATH" ]] && | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 182 | if grep -Fq 'org.pipewire.Telephony.AudioGateway1' "$AG_INTROSPECT" && | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 183 | grep -Fq 'Dial' "$AG_INTROSPECT" && | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 184 | grep -Fq 'HangupAll' "$AG_INTROSPECT" && | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 187 | else | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 191 | if grep -Fq 'org.ofono.VoiceCallManager' "$AG_INTROSPECT" && | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 194 | else | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 197 | else | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 202 | if [[ -n "$AG_PATH" ]] && | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 205 | CALL_PRESENCE="$(awk -v gateway="$AG_PATH" ' | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 206 | NR == 1 && ($1 == "a(oa{sv})" \|\| $1 == "a{oa{sv}}") && $2 ~ /^(0\|[1-9][0-9]*)$/ && length($2) <= 10 && $2 + 0 <= 4294967295 { | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 207 | if ($2 == "0" && NF == 2) print "no"; | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 208 | else if ($2 + 0 > 0 && $3 ~ "^\"" gateway "/call[0-9]+\"$") print "yes"; | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 209 | else print "unknown"; | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 212 | END { if (!found) print "unknown" } | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 215 | else | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 220 | if command -v pw-dump >/dev/null 2>&1 && | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 222 | if grep -Fqi "$DEVICE" "$PW_DUMP"; then | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 224 | else | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 227 | else | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |

## scripts/probe-hfp-audio.sh

Assertion families: [test_hfp_contract_extended](../scripts/tests/test_hfp_contract_extended.py), [test_probe_parameters](../scripts/tests/test_probe_parameters.py), [test_remaining_contracts](../scripts/tests/test_remaining_contracts.py).

| Source line | Decision / method | Assertion mapping |
| --- | --- | --- |
| 12 | usage() { | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 29 | if [[ "${1:-}" == "--help" \|\| "${1:-}" == "-h" ]]; then | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 31 | exit 0 | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 34 | if [[ $# -ne 0 ]]; then | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 37 | exit 2 | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 40 | if [[ ! "$DEVICE" =~ ^([[:xdigit:]]{2}:){5}[[:xdigit:]]{2}$ ]]; then | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 42 | exit 2 | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 45 | if [[ ! "$CONNECT_TIMEOUT" =~ ^[1-9][0-9]{0,17}$ ]] \|\| (( CONNECT_TIMEOUT > 922337203685477580 )); then | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 47 | exit 2 | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 50 | for command in awk bluetoothctl busctl grep head mktemp sed seq sleep timeout; do | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 51 | if ! command -v "$command" >/dev/null 2>&1; then | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 53 | exit 1 | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 57 | TMP_DIR="$(mktemp -d)" | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 65 | cleanup() { | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 68 | trap cleanup EXIT | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 69 | trap 'exit 130' INT | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 70 | trap 'exit 143' TERM | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 72 | bool_line() { | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 82 | info="$(bluetoothctl info "$DEVICE" 2>/dev/null \|\| true)" | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 83 | if [[ -z "$info" ]]; then | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 85 | exit 1 | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 89 | if grep -Eq '^[[:space:]]*Paired:[[:space:]]+yes$' <<<"$info"; then | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 91 | else | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 93 | exit 1 | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 96 | if grep -Fqi "$HFP_AG_UUID" <<<"$info"; then | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 98 | else | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 100 | exit 1 | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 103 | if command -v systemctl >/dev/null 2>&1 && | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 106 | else | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 110 | if command -v systemctl >/dev/null 2>&1 && | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 113 | else | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 122 | if [[ $CONNECT_STATUS -eq 124 ]]; then | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 124 | exit 1 | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 125 | elif grep -Fq 'Connection successful' "$CONNECT_LOG"; then | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 127 | elif grep -Eqi 'already connected\|connected: yes' "$CONNECT_LOG"; then | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 129 | else | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 134 | for _ in $(seq 1 50); do | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 135 | if busctl --user call "$TELEPHONY_SERVICE" "$TELEPHONY_MANAGER"     org.ofono.Manager GetModems >"$MODEMS_REPLY" 2>/dev/null; then | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 136 | AG_PATH="$(awk -F'"' ' | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 137 | { for (i = 2; i <= NF; i += 2) if ($i ~ /^\/org\/pipewire\/Telephony\/ag[0-9]+$/) seen[$i] = 1 } | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 138 | END { for (path in seen) { count++; last = path } if (count == 1) print last } | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 140 | [[ -n "$AG_PATH" ]] && break | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 145 | if [[ -z "$AG_PATH" ]]; then | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 147 | exit 1 | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 151 | if ! busctl --user introspect "$TELEPHONY_SERVICE" "$AG_PATH" >"$AG_INTROSPECT" 2>/dev/null; then | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 153 | exit 1 | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 156 | if grep -Fq "$TRANSPORT_IFACE" "$AG_INTROSPECT"; then | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 158 | else | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 160 | exit 1 | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 163 | if grep -Fq 'Activate' "$AG_INTROSPECT"; then | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 165 | else | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 169 | if busctl --user get-property "$TELEPHONY_SERVICE" "$AG_PATH"   "$TRANSPORT_IFACE" State >"$STATE_REPLY" 2>/dev/null; then | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 171 | else | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 173 | exit 1 | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 176 | if busctl --user get-property "$TELEPHONY_SERVICE" "$AG_PATH"   "$TRANSPORT_IFACE" Codec >"$CODEC_REPLY" 2>/dev/null; then | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 178 | else | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 180 | exit 1 | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 183 | if busctl --user get-property "$TELEPHONY_SERVICE" "$AG_PATH"   "$TRANSPORT_IFACE" RejectSCO >"$REJECT_REPLY" 2>/dev/null; then | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 185 | else | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 187 | exit 1 | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 190 | STATE="$(sed -nE 's/^s "(idle\|pending\|active\|error)"$/\1/p' "$STATE_REPLY")" | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 191 | CODEC="$(sed -nE 's/^y ([0-9]+)$/\1/p' "$CODEC_REPLY")" | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 192 | REJECT_SCO="$(sed -nE 's/^b (true\|false)$/\1/p' "$REJECT_REPLY")" | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 197 | case "${CODEC:-}" in | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 204 | case "${REJECT_SCO:-}" in | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 219 | if [[ -n "$STATE" && -n "$CODEC" && -n "$REJECT_SCO" ]]; then | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |
| 222 | else | test_hfp_contract_extended, test_probe_parameters, test_remaining_contracts |

## scripts/probe-hfp-call.sh

Assertion families: [test_hfp_contract_extended](../scripts/tests/test_hfp_contract_extended.py), [test_hfp_probe_contract](../scripts/tests/test_hfp_probe_contract.py), [test_probe_parameters](../scripts/tests/test_probe_parameters.py), [test_remaining_contracts](../scripts/tests/test_remaining_contracts.py), [test_getcalls_compatibility](../scripts/tests/test_getcalls_compatibility.py).

| Source line | Decision / method | Assertion mapping |
| --- | --- | --- |
| 13 | usage() { | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 27 | The destination is never printed. The probe refuses to dial if any call object | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 32 | while [[ $# -gt 0 ]]; do | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 33 | case "$1" in | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 40 | exit 0 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 45 | exit 2 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 50 | if [[ ! "$DEVICE" =~ ^([[:xdigit:]]{2}:){5}[[:xdigit:]]{2}$ ]]; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 52 | exit 2 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 55 | if [[ ! "$OBSERVE_SECONDS" =~ ^[1-9][0-9]{0,17}$ ]] \|\| (( OBSERVE_SECONDS > 922337203685477580 )); then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 57 | exit 2 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 60 | if [[ "$DO_DIAL" == yes ]] && | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 63 | exit 2 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 66 | for command in awk bluetoothctl busctl grep head mktemp sleep seq timeout; do | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 67 | if ! command -v "$command" >/dev/null 2>&1; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 69 | exit 1 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 73 | TMP_DIR="$(mktemp -d)" | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 82 | cleanup() { | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 84 | trap - EXIT INT TERM | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 86 | if [[ "$DIAL_ATTEMPTED" == yes && "$HANGUP_DONE" != yes && -n "$AG_PATH" ]]; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 88 | if timeout 8s busctl --user call "$TELEPHONY_SERVICE" "$AG_PATH" \ | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 91 | else | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 97 | exit "$status" | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 99 | trap cleanup EXIT | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 100 | trap 'exit 130' INT | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 101 | trap 'exit 143' TERM | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 103 | bool_line() { | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 111 | info="$(bluetoothctl info "$DEVICE" 2>/dev/null \|\| true)" | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 112 | if [[ -z "$info" ]] \|\| | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 115 | exit 1 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 119 | if ! grep -Fqi "$HFP_AG_UUID" <<<"$info"; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 121 | exit 1 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 130 | if [[ $CONNECT_STATUS -eq 124 ]]; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 132 | exit 1 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 133 | else | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 137 | for _ in $(seq 1 50); do | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 138 | if busctl --user call "$TELEPHONY_SERVICE" "$TELEPHONY_MANAGER"     org.ofono.Manager GetModems >"$MODEMS_REPLY" 2>/dev/null; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 139 | AG_PATH="$(awk -F'"' ' | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 140 | { for (i = 2; i <= NF; i += 2) if ($i ~ /^\/org\/pipewire\/Telephony\/ag[0-9]+$/) seen[$i] = 1 } | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 141 | END { for (path in seen) { count++; last = path } if (count == 1) print last } | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 143 | [[ -n "$AG_PATH" ]] && break | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 148 | if [[ -z "$AG_PATH" ]]; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 150 | exit 1 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 154 | if ! busctl --user introspect "$TELEPHONY_SERVICE" "$AG_PATH" 2>/dev/null \| | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 157 | exit 1 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 161 | if ! busctl --user call "$TELEPHONY_SERVICE" "$AG_PATH"   org.ofono.VoiceCallManager GetCalls >"$CALLS_REPLY" 2>/dev/null; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 163 | exit 1 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 165 | if ! grep -Eq '^a(\(oa\{sv\}\)\|\{oa\{sv\}\}) 0[[:space:]]*$' "$CALLS_REPLY" && | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 168 | exit 1 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 172 | if grep -qE '/org/pipewire/Telephony/ag[0-9]+/call[0-9]+' "$CALLS_REPLY"; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 176 | exit 1 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 180 | if [[ "$DO_DIAL" != yes ]]; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 185 | exit 0 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 199 | if [[ $DIAL_STATUS -ne 0 ]]; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 203 | exit 1 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 208 | for _ in $(seq 1 "$((OBSERVE_SECONDS * 10))"); do | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 209 | if busctl --user call "$TELEPHONY_SERVICE" "$AG_PATH"     org.ofono.VoiceCallManager GetCalls >"$CALLS_REPLY" 2>/dev/null && | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 224 | if [[ $HANGUP_STATUS -eq 0 ]]; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 227 | else | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 231 | exit 1 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 236 | if [[ "$CALL_SEEN" == yes ]]; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 239 | else | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |

## scripts/probe-hfp-sco.sh

Assertion families: [test_hfp_contract_extended](../scripts/tests/test_hfp_contract_extended.py), [test_hfp_probe_contract](../scripts/tests/test_hfp_probe_contract.py), [test_probe_parameters](../scripts/tests/test_probe_parameters.py), [test_remaining_contracts](../scripts/tests/test_remaining_contracts.py), [test_getcalls_compatibility](../scripts/tests/test_getcalls_compatibility.py), [test_hfp_node_classification](../scripts/tests/test_hfp_node_classification.py).

| Source line | Decision / method | Assertion mapping |
| --- | --- | --- |
| 19 | usage() { | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 29 | NATIVEPAIR_SCO_STATE_TIMEOUT    Condition wait limit for SCO activation (default 15). | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 30 | NATIVEPAIR_CALL_ACTIVE_TIMEOUT  Condition wait limit for remote answer (default 30). | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 43 | while [[ $# -gt 0 ]]; do | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 44 | case "$1" in | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 51 | exit 0 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 56 | exit 2 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 61 | if [[ ! "$DEVICE" =~ ^([[:xdigit:]]{2}:){5}[[:xdigit:]]{2}$ ]]; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 63 | exit 2 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 66 | for value_name in CONNECT_TIMEOUT STATE_TIMEOUT CALL_ACTIVE_TIMEOUT HUMAN_WINDOW; do | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 68 | if [[ ! "$value" =~ ^[1-9][0-9]{0,17}$ ]] \|\| (( value > 922337203685477580 )); then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 70 | exit 2 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 74 | if [[ "$DO_DIAL" == yes ]] && | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 77 | exit 2 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 80 | for command in awk bluetoothctl busctl cat grep head mktemp python3 pw-dump sed seq sleep timeout wpctl; do | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 81 | if ! command -v "$command" >/dev/null 2>&1; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 83 | exit 1 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 87 | TMP_DIR="$(mktemp -d)" | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 106 | cleanup() { | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 108 | trap - EXIT INT TERM | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 110 | if [[ "$DIAL_ATTEMPTED" == yes && "$HANGUP_DONE" != yes && -n "$AG_PATH" ]]; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 112 | if timeout 8s busctl --user call "$TELEPHONY_SERVICE" "$AG_PATH" \ | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 115 | else | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 121 | exit "$status" | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 123 | trap cleanup EXIT | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 124 | trap 'exit 130' INT | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 125 | trap 'exit 143' TERM | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 127 | bool_line() { | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 131 | read_transport_state() { | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 132 | if ! busctl --user get-property "$TELEPHONY_SERVICE" "$AG_PATH"     "$TRANSPORT_IFACE" State >"$STATE_REPLY" 2>/dev/null; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 133 | return 1 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 138 | refresh_call_snapshot() { | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 142 | if ! busctl --user call "$TELEPHONY_SERVICE" "$AG_PATH" \ | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 144 | return 1 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 147 | CALL_PATH="$( | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 149 | grep -oE '/org/pipewire/Telephony/ag[0-9]+/call[0-9]+' "$CALLS_REPLY" \|\| true | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 154 | if [[ -z "$CALL_PATH" ]]; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 155 | return 2 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 158 | for state in active dialing alerting incoming waiting held disconnected; do | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 159 | if grep -Eq "\"State\"[[:space:]]+s[[:space:]]+\"$state\"" "$CALLS_REPLY"; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 161 | return 0 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 165 | for iface in org.pipewire.Telephony.Call1 org.ofono.VoiceCall; do | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 166 | if busctl --user get-property "$TELEPHONY_SERVICE" "$CALL_PATH" \ | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 168 | CALL_STATE="$(sed -nE 's/^s "(active\|dialing\|alerting\|incoming\|waiting\|held\|disconnected)"$/\1/p' "$CALL_STATE_REPLY")" | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 169 | if [[ -n "$CALL_STATE" ]]; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 170 | return 0 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 175 | return 0 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 178 | inspect_hfp_nodes() { | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 179 | if ! pw-dump >"$PW_DUMP" 2>/dev/null; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 180 | return 1 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 183 | python3 - "$PW_DUMP" "$DEVICE" "$(dirname -- "${BASH_SOURCE[0]}")" >"$NODE_RESULT" <<'PY' | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 194 | sys.exit(1) | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 200 | for obj in data: | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 203 | if props.get("api.bluez5.address") != device: | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 205 | if not is_hfp(props): | test_hfp_node_classification |
| 210 | if direction == "source": | test_hfp_node_classification |
| 212 | elif direction == "sink": | test_hfp_node_classification |
| 216 | print(f"hfp_source_node_present={'yes' if source else 'no'}") | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 217 | print(f"hfp_sink_node_present={'yes' if sink else 'no'}") | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 218 | print(f"hfp_nodes_ready={'yes' if count >= 2 and source and sink else 'no'}") | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 226 | info="$(bluetoothctl info "$DEVICE" 2>/dev/null \|\| true)" | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 227 | if [[ -z "$info" ]] \|\| | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 230 | exit 1 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 234 | if ! grep -Fqi "$HFP_AG_UUID" <<<"$info"; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 236 | exit 1 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 245 | if [[ $CONNECT_STATUS -eq 124 ]]; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 247 | exit 1 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 248 | elif grep -Fq 'Connection successful' "$CONNECT_LOG"; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 250 | elif grep -Eqi 'already connected\|connected: yes' "$CONNECT_LOG"; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 252 | else | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 256 | for _ in $(seq 1 50); do | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 257 | if busctl --user call "$TELEPHONY_SERVICE" "$TELEPHONY_MANAGER"     org.ofono.Manager GetModems >"$MODEMS_REPLY" 2>/dev/null; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 258 | AG_PATH="$(awk -F'"' ' | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 259 | { for (i = 2; i <= NF; i += 2) if ($i ~ /^\/org\/pipewire\/Telephony\/ag[0-9]+$/) seen[$i] = 1 } | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 260 | END { for (path in seen) { count++; last = path } if (count == 1) print last } | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 262 | [[ -n "$AG_PATH" ]] && break | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 267 | if [[ -z "$AG_PATH" ]]; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 269 | exit 1 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 273 | if ! busctl --user call "$TELEPHONY_SERVICE" "$AG_PATH"   org.ofono.VoiceCallManager GetCalls >"$CALLS_REPLY" 2>/dev/null; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 275 | exit 1 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 277 | if ! grep -Eq '^a(\(oa\{sv\}\)\|\{oa\{sv\}\}) 0[[:space:]]*$' "$CALLS_REPLY" && | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 280 | exit 1 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 284 | if grep -qE '/org/pipewire/Telephony/ag[0-9]+/call[0-9]+' "$CALLS_REPLY"; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 288 | exit 1 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 292 | if ! busctl --user introspect "$TELEPHONY_SERVICE" "$AG_PATH" 2>/dev/null \| | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 295 | exit 1 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 299 | if ! busctl --user introspect "$TELEPHONY_SERVICE" "$AG_PATH" 2>/dev/null \| | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 302 | exit 1 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 306 | if ! busctl --user get-property "$TELEPHONY_SERVICE" "$AG_PATH"   "$TRANSPORT_IFACE" RejectSCO >"$REJECT_REPLY" 2>/dev/null; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 308 | exit 1 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 312 | if grep -Fq 'b true' "$REJECT_REPLY"; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 316 | exit 1 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 317 | elif grep -Fq 'b false' "$REJECT_REPLY"; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 319 | else | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 322 | exit 1 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 325 | INITIAL_STATE="$(read_transport_state \|\| true)" | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 328 | if [[ "$DO_DIAL" != yes ]]; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 334 | exit 0 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 348 | if [[ $DIAL_STATUS -ne 0 ]]; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 352 | exit 1 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 357 | for _ in $(seq 1 "$((STATE_TIMEOUT * 10))"); do | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 358 | if refresh_call_snapshot && [[ -n "$CALL_PATH" ]]; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 366 | if [[ "$CALL_SEEN" != yes ]]; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 369 | exit 1 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 375 | for _ in $(seq 1 "$((CALL_ACTIVE_TIMEOUT * 10))"); do | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 376 | if refresh_call_snapshot; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 378 | if [[ "$LAST_CALL_STATE" == active ]]; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 389 | if [[ "$CALL_ACTIVE_SEEN" != yes ]]; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 392 | exit 1 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 398 | TRANSPORT_STATE_BEFORE_ACTIVATE="$(read_transport_state \|\| true)" | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 407 | case "$TRANSPORT_STATE_BEFORE_ACTIVATE" in | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 418 | for _ in $(seq 1 "$((STATE_TIMEOUT * 10))"); do | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 419 | LAST_STATE="$(read_transport_state \|\| true)" | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 420 | if [[ "$LAST_STATE" == active ]]; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 424 | [[ "$LAST_STATE" == idle \|\| "$LAST_STATE" == error ]] && break | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 438 | if [[ $ACTIVATE_STATUS -ne 0 ]]; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 441 | ACTIVATE_ERROR_CLASS="$( | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 443 | grep -oE 'org\.pipewire\.Telephony\.Error\.(InvalidState\|InvalidFormat\|NotSupported\|InProgress\|Failed\|CME)\|org\.freedesktop\.DBus\.Error\.(InvalidArgs\|Failed\|NoReply\|Timeout\|AccessDenied\|ServiceUnknown)' "$ACTIVATE_REPLY" \|\| | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 447 | if [[ -z "$ACTIVATE_ERROR_CLASS" ]]; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 448 | if grep -Eqi 'timed out\|timeout' "$ACTIVATE_REPLY"; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 450 | elif grep -Eqi 'invalid state\|already active' "$ACTIVATE_REPLY"; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 452 | else | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 457 | LAST_STATE="$(read_transport_state \|\| true)" | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 461 | for _ in $(seq 1 15); do | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 462 | [[ "$LAST_STATE" == active ]] && { ACTIVE_SEEN=yes; break; } | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 463 | [[ "$LAST_STATE" == error ]] && break | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 465 | LAST_STATE="$(read_transport_state \|\| true)" | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 467 | if [[ "$LAST_STATE" == active ]]; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 471 | else | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 482 | if [[ "$ACTIVATE_INVOKED" != yes ]]; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 486 | if [[ "$ACTIVE_SEEN" != yes && "$ACTIVATE_STATUS" != not_called && "$ACTIVATE_STATUS" != 0 ]]; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 491 | exit 1 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 494 | if [[ "$ACTIVE_SEEN" != yes && "$ACTIVATE_STATUS" != not_called && "$ACTIVATE_STATUS" == 0 ]]; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 495 | for _ in $(seq 1 "$((STATE_TIMEOUT * 10))"); do | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 496 | LAST_STATE="$(read_transport_state \|\| true)" | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 497 | if [[ "$LAST_STATE" == active ]]; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 501 | [[ "$LAST_STATE" == error ]] && break | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 510 | if [[ "$ACTIVE_SEEN" != yes ]]; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 513 | exit 1 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 517 | for _ in $(seq 1 "$((STATE_TIMEOUT * 10))"); do | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 518 | if inspect_hfp_nodes && grep -Fq 'hfp_nodes_ready=yes' "$NODE_RESULT"; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 525 | if [[ -s "$NODE_RESULT" ]]; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 527 | else | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 536 | if [[ "$NODES_READY" != yes ]]; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 542 | if [[ "$SNAPSHOT_STATUS" == 0 ]]; then | test_hfp_node_classification |
| 544 | elif [[ "$SNAPSHOT_STATUS" == 2 ]] && | test_hfp_node_classification |
| 549 | NODE_WAIT_TRANSPORT_STATE="$(read_transport_state \|\| true)" | test_hfp_node_classification |
| 553 | exit 1 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 565 | if [[ $HANGUP_STATUS -ne 0 ]]; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 569 | exit 1 | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 575 | if [[ "$ACTIVATE_RESULT" == error_but_transport_active ]]; then | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |
| 577 | else | test_hfp_contract_extended, test_hfp_probe_contract, test_probe_parameters, test_remaining_contracts, test_getcalls_compatibility |

## scripts/probe-map-events.sh

Assertion families: [test_map_events_contract](../scripts/tests/test_map_events_contract.py), [test_obex_contract](../scripts/tests/test_obex_contract.py), [test_probe_parameters](../scripts/tests/test_probe_parameters.py), [test_remaining_contracts](../scripts/tests/test_remaining_contracts.py).

| Source line | Decision / method | Assertion mapping |
| --- | --- | --- |
| 9 | usage() { | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 24 | waits for BlueZ to expose a new org.bluez.obex.Message1 object. | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 29 | deleted on exit. The script never prints Bluetooth addresses, phone aliases, | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 34 | while [[ $# -gt 0 ]]; do | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 35 | case "$1" in | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 38 | exit 0 | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 43 | exit 2 | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 48 | if [[ ! "$DEVICE" =~ ^([[:xdigit:]]{2}:){5}[[:xdigit:]]{2}$ ]]; then | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 50 | exit 2 | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 53 | for value_name in EVENT_TIMEOUT CONNECT_TIMEOUT; do | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 55 | if [[ ! "$value" =~ ^[1-9][0-9]{0,17}$ ]] \|\| (( value > 922337203685477580 )); then | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 57 | exit 2 | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 61 | for command in busctl bluetoothctl obexctl stdbuf mktemp python3; do | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 62 | if ! command -v "$command" >/dev/null 2>&1; then | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 64 | exit 1 | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 72 | if ! busctl --user list 2>/dev/null \| awk '{print $1}' \| grep -Fxq org.bluez.obex; then | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 74 | exit 1 | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 78 | if ! bluetoothctl info "$DEVICE" 2>/dev/null \| grep -Eq '^[[:space:]]*Paired:[[:space:]]+yes$'; then | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 80 | exit 1 | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 84 | if bluetoothctl show 2>/dev/null \| | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 88 | else | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 92 | TMP_DIR="$(mktemp -d)" | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 102 | cleanup() { | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 104 | trap - EXIT INT TERM | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 105 | trap '' PIPE | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 107 | if [[ -n "$OBEX_FD" ]]; then | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 108 | printf 'disconnect\nquit\n' >&"$OBEX_FD" 2>/dev/null \|\| true | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 109 | exec {OBEX_FD}>&- 2>/dev/null \|\| true | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 112 | if [[ -n "$OBEX_PID" ]] && kill -0 "$OBEX_PID" 2>/dev/null; then | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 113 | for _ in 1 2 3 4 5; do | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 114 | kill -0 "$OBEX_PID" 2>/dev/null \|\| break | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 117 | kill "$OBEX_PID" 2>/dev/null \|\| true | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 118 | wait "$OBEX_PID" 2>/dev/null \|\| true | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 121 | if [[ -n "$MONITOR_PID" ]] && kill -0 "$MONITOR_PID" 2>/dev/null; then | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 122 | kill "$MONITOR_PID" 2>/dev/null \|\| true | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 123 | wait "$MONITOR_PID" 2>/dev/null \|\| true | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 127 | exit "$status" | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 129 | trap cleanup EXIT | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 130 | trap 'exit 130' INT | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 131 | trap 'exit 143' TERM | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 139 | for _ in {1..50}; do | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 140 | if grep -Fq 'Monitoring bus message stream' "$MONITOR_LOG"; then | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 144 | kill -0 "$MONITOR_PID" 2>/dev/null \|\| break | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 148 | if [[ "$MONITOR_READY" != yes ]] \|\| ! kill -0 "$MONITOR_PID" 2>/dev/null; then | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 150 | exit 1 | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 158 | wait_for_log() { | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 164 | while (( elapsed < timeout_seconds * 10 )); do | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 165 | if grep -Eq "$pattern" "$file" 2>/dev/null; then | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 166 | return 0 | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 172 | return 1 | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 175 | if ! wait_for_log "$OBEX_LOG" 'Client .*/org/bluez/obex\|\[NEW\].*Client' 5; then | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 177 | exit 1 | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 183 | if ! wait_for_log "$OBEX_LOG" 'Connection successful\|Failed to connect' "$CONNECT_TIMEOUT"; then | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 186 | exit 1 | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 189 | if grep -Fq 'Failed to connect' "$OBEX_LOG"; then | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 192 | exit 1 | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 195 | SESSION_PATH="$( | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 200 | if [[ -z "$SESSION_PATH" ]]; then | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 203 | exit 1 | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 206 | if ! wait_for_log "$OBEX_LOG" 'MessageAccess /org/bluez/obex/client/session\|\[NEW\].*MessageAccess' 2; then | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 209 | exit 1 | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 215 | MONITOR_PARSER="$(dirname -- "${BASH_SOURCE[0]}")/probe_obex_monitor.py" | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 218 | for _ in {1..30}; do | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 222 | [[ "$registration_transfer_status" == complete \|\| "$registration_transfer_status" == error ]] && break | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 231 | baseline_monitor_messages="$(python3 "$MONITOR_PARSER" --messages "$MONITOR_LOG" "$SESSION_PATH")" | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 232 | baseline_obexctl_messages="$(python3 "$MONITOR_PARSER" --obex-messages "$OBEX_LOG" "$SESSION_PATH")" | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 236 | while (( elapsed < EVENT_TIMEOUT * 10 )); do | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 237 | current_monitor_messages="$(python3 "$MONITOR_PARSER" --messages "$MONITOR_LOG" "$SESSION_PATH")" | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 238 | current_obexctl_messages="$(python3 "$MONITOR_PARSER" --obex-messages "$OBEX_LOG" "$SESSION_PATH")" | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 240 | if (( current_monitor_messages > baseline_monitor_messages \|\| | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 246 | if ! kill -0 "$OBEX_PID" 2>/dev/null; then | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 250 | exit 1 | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 253 | if ! kill -0 "$MONITOR_PID" 2>/dev/null; then | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 257 | exit 1 | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 266 | if [[ "$event_observed" == yes ]]; then | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 269 | if [[ "$registration_transfer_status" == complete ]]; then | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 271 | else | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 274 | else | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 276 | if [[ "$registration_transfer_status" != complete ]]; then | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 278 | else | test_map_events_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |

## scripts/probe-map-sdp.sh

Assertion families: [test_discovery_contract](../scripts/tests/test_discovery_contract.py), [test_probe_parameters](../scripts/tests/test_probe_parameters.py), [test_remaining_contracts](../scripts/tests/test_remaining_contracts.py).

| Source line | Decision / method | Assertion mapping |
| --- | --- | --- |
| 3 | trap 'exit 130' INT | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 4 | trap 'exit 143' TERM | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 9 | usage() { | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 20 | temporary file and deleted on exit. The Bluetooth address and service payload | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 25 | while [[ $# -gt 0 ]]; do | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 26 | case "$1" in | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 29 | exit 0 | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 34 | exit 2 | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 39 | if [[ ! "$DEVICE" =~ ^([[:xdigit:]]{2}:){5}[[:xdigit:]]{2}$ ]]; then | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 41 | exit 2 | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 44 | for command in sdptool timeout mktemp; do | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 45 | if ! command -v "$command" >/dev/null 2>&1; then | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 47 | exit 1 | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 54 | SDP_OUT="$(mktemp)" | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 55 | trap 'rm -f "$SDP_OUT"' EXIT | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 62 | if [[ $SDP_STATUS -eq 124 ]]; then | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 65 | exit 1 | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 66 | elif [[ $SDP_STATUS -ne 0 ]]; then | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 69 | exit 1 | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 74 | if grep -Eqi '<attribute[^>]+id="0x0315"\|<attribute[^>]+id="0x315"' "$SDP_OUT"; then | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 76 | else | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 80 | if grep -Eqi '<attribute[^>]+id="0x0316"\|<attribute[^>]+id="0x316"' "$SDP_OUT"; then | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 82 | else | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 86 | if grep -Eqi '<attribute[^>]+id="0x0317"\|<attribute[^>]+id="0x317"' "$SDP_OUT"; then | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 88 | else | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 92 | if grep -Eqi 'uuid[^>]+value="0x1132"\|uuid[^>]+value="00001132' "$SDP_OUT"; then | test_discovery_contract, test_probe_parameters, test_remaining_contracts |
| 94 | else | test_discovery_contract, test_probe_parameters, test_remaining_contracts |

## scripts/probe-map-send.sh

Assertion families: [test_map_send_contract](../scripts/tests/test_map_send_contract.py), [test_obex_contract](../scripts/tests/test_obex_contract.py), [test_probe_parameters](../scripts/tests/test_probe_parameters.py), [test_remaining_contracts](../scripts/tests/test_remaining_contracts.py).

| Source line | Decision / method | Assertion mapping |
| --- | --- | --- |
| 12 | usage() { | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 29 | risk. Temporary payload and D-Bus logs are deleted on exit. | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 33 | while [[ $# -gt 0 ]]; do | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 34 | case "$1" in | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 41 | exit 0 | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 46 | exit 2 | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 51 | if [[ ! "$DEVICE" =~ ^([[:xdigit:]]{2}:){5}[[:xdigit:]]{2}$ ]]; then | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 53 | exit 2 | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 56 | if [[ ! "$RECIPIENT" =~ ^\+[1-9][0-9]{6,14}$ ]]; then | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 58 | exit 2 | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 61 | for value_name in CONNECT_TIMEOUT TRANSFER_TIMEOUT; do | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 63 | if [[ ! "$value" =~ ^[1-9][0-9]{0,17}$ ]] \|\| (( value > 922337203685477580 )); then | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 65 | exit 2 | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 69 | for command in busctl bluetoothctl obexctl stdbuf mktemp wc tail grep sed od tr python3; do | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 70 | if ! command -v "$command" >/dev/null 2>&1; then | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 72 | exit 1 | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 80 | if ! busctl --user list 2>/dev/null \| awk '{print $1}' \| grep -Fxq org.bluez.obex; then | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 82 | exit 1 | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 86 | if ! bluetoothctl info "$DEVICE" 2>/dev/null \| grep -Eq '^[[:space:]]*Paired:[[:space:]]+yes$'; then | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 88 | exit 1 | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 92 | TMP_DIR="$(mktemp -d)" | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 104 | cleanup() { | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 106 | trap - EXIT INT TERM | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 107 | trap '' PIPE | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 109 | if [[ -n "$OBEX_FD" ]]; then | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 110 | printf 'disconnect\nquit\n' >&"$OBEX_FD" 2>/dev/null \|\| true | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 111 | exec {OBEX_FD}>&- 2>/dev/null \|\| true | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 114 | if [[ -n "$OBEX_PID" ]] && kill -0 "$OBEX_PID" 2>/dev/null; then | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 115 | for _ in 1 2 3 4 5; do | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 116 | kill -0 "$OBEX_PID" 2>/dev/null \|\| break | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 119 | kill "$OBEX_PID" 2>/dev/null \|\| true | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 120 | wait "$OBEX_PID" 2>/dev/null \|\| true | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 123 | if [[ -n "$MONITOR_PID" ]] && kill -0 "$MONITOR_PID" 2>/dev/null; then | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 124 | kill "$MONITOR_PID" 2>/dev/null \|\| true | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 125 | wait "$MONITOR_PID" 2>/dev/null \|\| true | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 129 | exit "$status" | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 131 | trap cleanup EXIT | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 132 | trap 'exit 130' INT | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 133 | trap 'exit 143' TERM | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 139 | for _ in {1..50}; do | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 140 | if grep -Fq 'Monitoring bus message stream' "$MONITOR_LOG"; then | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 144 | kill -0 "$MONITOR_PID" 2>/dev/null \|\| break | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 148 | if [[ "$MONITOR_READY" != yes ]] \|\| ! kill -0 "$MONITOR_PID" 2>/dev/null; then | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 150 | exit 1 | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 158 | wait_for_log() { | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 164 | while (( elapsed < timeout_seconds * 10 )); do | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 165 | if grep -Eq "$pattern" "$file" 2>/dev/null; then | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 166 | return 0 | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 168 | if [[ "$file" == "$OBEX_LOG" ]] && ! kill -0 "$OBEX_PID" 2>/dev/null; then | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 169 | return 1 | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 175 | return 1 | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 178 | if ! wait_for_log "$OBEX_LOG" 'Client .*/org/bluez/obex\|\[NEW\].*Client' 5; then | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 180 | exit 1 | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 186 | if ! wait_for_log "$OBEX_LOG" 'Connection successful\|Failed to connect' "$CONNECT_TIMEOUT"; then | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 189 | exit 1 | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 192 | if grep -Fq 'Failed to connect' "$OBEX_LOG"; then | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 195 | exit 1 | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 198 | SESSION_PATH="$( | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 203 | if [[ -z "$SESSION_PATH" ]]; then | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 206 | exit 1 | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 209 | if ! wait_for_log "$OBEX_LOG" 'MessageAccess /org/bluez/obex/client/session\|\[NEW\].*MessageAccess' 2; then | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 212 | exit 1 | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 217 | if busctl --user get-property org.bluez.obex "$SESSION_PATH"   org.bluez.obex.MessageAccess1 SupportedTypes >"$SUPPORTED_TYPES" 2>/dev/null && | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 220 | else | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 222 | exit 1 | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 225 | if ! busctl --user call org.bluez.obex "$SESSION_PATH"   org.bluez.obex.MessageAccess1 SetFolder s telecom >/dev/null 2>&1; then | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 227 | exit 1 | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 231 | if ! busctl --user call org.bluez.obex "$SESSION_PATH"   org.bluez.obex.MessageAccess1 SetFolder s msg >/dev/null 2>&1; then | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 233 | exit 1 | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 237 | MESSAGE_BYTES="$(printf '%s' "$MESSAGE_TEXT" \| wc -c)" | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 240 | MSG_LENGTH="$((MESSAGE_BYTES + 22))" | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 267 | if ! grep -Fqx $'BEGIN:MSG\r' "$BMSG_FILE" \|\| | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 268 | ! grep -Fqx $'END:MSG\r' "$BMSG_FILE" \|\| | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 269 | ! grep -Fqx $'END:BBODY\r' "$BMSG_FILE" \|\| | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 270 | [[ "$(tail -c 2 "$BMSG_FILE" \| od -An -t x1 \| tr -d '[:space:]')" != "0d0a" ]]; then | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 273 | exit 1 | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 282 | if [[ "$DO_SEND" != yes ]]; then | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 286 | exit 0 | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 291 | MONITOR_BASELINE="$(wc -l <"$MONITOR_LOG")" | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 298 | if [[ $PUSH_STATUS -ne 0 ]]; then | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 302 | exit 1 | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 306 | TRANSFER_PATH="$( | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 311 | if [[ -n "$TRANSFER_PATH" ]]; then | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 313 | else | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 319 | while (( elapsed < TRANSFER_TIMEOUT * 10 )); do | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 321 | tail -n "+$((MONITOR_BASELINE + 1))" "$MONITOR_LOG" >"$NEW_LOG" 2>/dev/null \|\| true | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 323 | transfer_result="$(python3 "$(dirname -- "${BASH_SOURCE[0]}")/probe_obex_monitor.py" "$NEW_LOG" "$TRANSFER_PATH")" | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 324 | if [[ "$transfer_result" == complete \|\| "$transfer_result" == error ]]; then | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 328 | if ! kill -0 "$OBEX_PID" 2>/dev/null; then | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 339 | case "$transfer_result" in | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 347 | exit 1 | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 352 | exit 1 | test_map_send_contract, test_obex_contract, test_probe_parameters, test_remaining_contracts |

## scripts/probe-mns.sh

Assertion families: [test_discovery_contract](../scripts/tests/test_discovery_contract.py), [test_mns_process_contract](../scripts/tests/test_mns_process_contract.py), [test_remaining_contracts](../scripts/tests/test_remaining_contracts.py).

| Source line | Decision / method | Assertion mapping |
| --- | --- | --- |
| 3 | trap 'exit 130' INT | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 4 | trap 'exit 143' TERM | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 9 | command_present() { | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 10 | if command -v "$1" >/dev/null 2>&1; then | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 12 | else | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 17 | bool_line() { | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 21 | bool_line bluetoothctl_present "$(command_present bluetoothctl)" | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 22 | bool_line busctl_present "$(command_present busctl)" | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 23 | bool_line sdptool_present "$(command_present sdptool)" | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 24 | bool_line strings_present "$(command_present strings)" | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 25 | bool_line dpkg_query_present "$(command_present dpkg-query)" | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 27 | if command -v dpkg-query >/dev/null 2>&1; then | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 28 | package_version="$(dpkg-query -W -f='${Version}' bluez-obexd 2>/dev/null \|\| true)" | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 30 | else | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 34 | if command -v busctl >/dev/null 2>&1 && | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 37 | else | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 41 | if command -v busctl >/dev/null 2>&1 && | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 44 | else | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 48 | OBEX_PID="$( | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 50 | head -n 1 \|\| | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 54 | if [[ -n "$OBEX_PID" && -r "/proc/$OBEX_PID/exe" ]]; then | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 56 | OBEX_EXE="$(readlink -f "/proc/$OBEX_PID/exe" 2>/dev/null \|\| true)" | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 57 | else | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 63 | if [[ -n "$OBEX_PID" && -r "/proc/$OBEX_PID/cmdline" ]]; then | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 64 | CMDLINE="$(tr '\0' ' ' < "/proc/$OBEX_PID/cmdline")" | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 65 | if grep -Eq -- '(^\|[[:space:]])--noplugin(=\|[[:space:]]+)([^[:space:],]+,)*mns(,\|[[:space:]]\|$)' <<<"$CMDLINE"; then | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 67 | else | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 73 | if [[ -n "$OBEX_EXE" && -r "$OBEX_EXE" ]] && command -v strings >/dev/null 2>&1; then | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 74 | STRINGS_OUT="$(mktemp)" | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 76 | trap 'rm -f "$STRINGS_OUT" "${SDP_OUT:-}"' EXIT | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 79 | if grep -Fq 'x-bt/MAP-NotificationRegistration' "$STRINGS_OUT"; then | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 81 | else | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 85 | if grep -Fq 'x-bt/MAP-event-report' "$STRINGS_OUT"; then | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 87 | else | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 91 | if grep -Fq 'Message Notification server' "$STRINGS_OUT"; then | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 93 | else | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 97 | if grep -Fq 'x-bt/MAP-event-report' "$STRINGS_OUT" \|\| | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 100 | else | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 103 | else | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 109 | trap 'rm -f "${SDP_OUT:-}"' EXIT | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 112 | if command -v bluetoothctl >/dev/null 2>&1 && | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 117 | else | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 121 | if command -v sdptool >/dev/null 2>&1; then | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 122 | SDP_OUT="$(mktemp)" | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 129 | if [[ $SDP_STATUS -eq 0 ]]; then | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 132 | if grep -Eqi 'Message Notification\|0x1133\|00001133-0000-1000-8000-00805f9b34fb' "$SDP_OUT"; then | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 134 | else | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 137 | else | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 139 | if grep -Eqi 'permission\|not permitted\|access denied' "$SDP_OUT"; then | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 141 | elif grep -Eqi 'connection refused\|failed to connect\|no such file\|not available\|not found' "$SDP_OUT"; then | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 143 | else | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 148 | else | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 155 | if [[ -n "${STRINGS_OUT:-}" && "$MNS_EXPLICITLY_DISABLED" == no ]] && | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 156 | grep -Fq 'x-bt/MAP-NotificationRegistration' "$STRINGS_OUT" && | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |
| 157 | grep -Fq 'x-bt/MAP-event-report' "$STRINGS_OUT" && | test_discovery_contract, test_mns_process_contract, test_remaining_contracts |

## scripts/probe-obex-read.sh

Assertion families: [test_obex_contract](../scripts/tests/test_obex_contract.py), [test_probe_parameters](../scripts/tests/test_probe_parameters.py), [test_remaining_contracts](../scripts/tests/test_remaining_contracts.py).

| Source line | Decision / method | Assertion mapping |
| --- | --- | --- |
| 9 | usage() { | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 20 | Raw D-Bus responses are kept only in a temporary directory and deleted on exit. | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 26 | while [[ $# -gt 0 ]]; do | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 27 | case "$1" in | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 29 | [[ $# -ge 2 ]] \|\| { echo "--device requires a Bluetooth address." >&2; exit 2; } | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 34 | [[ $# -ge 2 ]] \|\| { echo "--target requires map or pbap." >&2; exit 2; } | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 40 | exit 0 | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 45 | exit 2 | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 50 | if [[ ! "$DEVICE" =~ ^([[:xdigit:]]{2}:){5}[[:xdigit:]]{2}$ ]]; then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 52 | exit 2 | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 55 | if [[ ! "$CONNECT_TIMEOUT" =~ ^[1-9][0-9]{0,17}$ ]] \|\| (( CONNECT_TIMEOUT > 922337203685477580 )); then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 57 | exit 2 | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 60 | case "$TARGET" in | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 71 | exit 2 | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 75 | for command in busctl bluetoothctl obexctl stdbuf mktemp; do | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 76 | if ! command -v "$command" >/dev/null 2>&1; then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 78 | exit 1 | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 87 | if ! busctl --user list 2>/dev/null \| awk '{print $1}' \| grep -Fxq org.bluez.obex; then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 89 | exit 1 | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 93 | if ! bluetoothctl info "$DEVICE" 2>/dev/null \| grep -Eq '^[[:space:]]*Paired:[[:space:]]+yes$'; then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 95 | exit 1 | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 99 | TMP_DIR="$(mktemp -d)" | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 107 | cleanup() { | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 109 | trap - EXIT INT TERM | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 110 | trap '' PIPE | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 112 | if [[ -n "$OBEX_FD" ]]; then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 113 | printf 'disconnect\nquit\n' >&"$OBEX_FD" 2>/dev/null \|\| true | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 114 | exec {OBEX_FD}>&- 2>/dev/null \|\| true | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 117 | if [[ -n "$OBEX_PID" ]] && kill -0 "$OBEX_PID" 2>/dev/null; then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 118 | for _ in 1 2 3 4 5; do | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 119 | kill -0 "$OBEX_PID" 2>/dev/null \|\| break | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 122 | kill "$OBEX_PID" 2>/dev/null \|\| true | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 123 | wait "$OBEX_PID" 2>/dev/null \|\| true | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 127 | exit "$status" | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 129 | trap cleanup EXIT | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 130 | trap 'exit 130' INT | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 131 | trap 'exit 143' TERM | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 138 | wait_for_log() { | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 143 | while (( elapsed < timeout_seconds * 10 )); do | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 144 | if grep -Eq "$pattern" "$OBEX_LOG" 2>/dev/null; then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 145 | return 0 | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 147 | if ! kill -0 "$OBEX_PID" 2>/dev/null; then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 148 | return 1 | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 154 | return 1 | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 157 | if ! wait_for_log 'Client .*/org/bluez/obex\|\[NEW\].*Client' 5; then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 159 | exit 1 | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 165 | if ! wait_for_log 'Connection successful\|Failed to connect' "$CONNECT_TIMEOUT"; then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 168 | exit 1 | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 171 | if grep -Fq 'Failed to connect' "$OBEX_LOG"; then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 174 | exit 1 | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 177 | SESSION_PATH="$( | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 182 | if [[ -z "$SESSION_PATH" ]]; then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 185 | exit 1 | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 188 | if ! wait_for_log "\[NEW\].*$EXPECTED_PROXY_LABEL\|$EXPECTED_PROXY_LABEL /org/bluez/obex/client/session" 2; then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 191 | exit 1 | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 194 | if ! busctl --user introspect   org.bluez.obex   "$SESSION_PATH"   "$EXPECTED_INTERFACE" >/dev/null 2>&1; then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 197 | exit 1 | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 202 | array_count() { | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 206 | NR == 1 && $1 == signature && $2 ~ /^(0\|[1-9][0-9]*)$/ && length($2) <= 10 && $2 + 0 <= 4294967295 { print $2; found = 1 } | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 207 | END { if (!found) print "unknown" } | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 211 | dbus_error_name() { | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 213 | grep -Eo 'org\.bluez\.obex\.Error\.[A-Za-z]+' "$file" \| head -n 1 \|\| true | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 216 | call_to_file() { | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 225 | return "$status" | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 228 | if [[ "$TARGET" == "map" ]]; then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 230 | if call_to_file "$FOLDERS_OUT"     org.bluez.obex "$SESSION_PATH" org.bluez.obex.MessageAccess1     ListFolders 'a{sv}' 1 MaxCount q 16; then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 232 | count="$(array_count "$FOLDERS_OUT" 'aa{sv}')" | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 233 | if [[ "$count" == "unknown" ]]; then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 235 | elif (( count > 0 )); then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 237 | else | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 240 | else | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 242 | error_name="$(dbus_error_name "$FOLDERS_OUT")" | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 244 | exit 1 | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 248 | if call_to_file "$TELECOM_OUT"     org.bluez.obex "$SESSION_PATH" org.bluez.obex.MessageAccess1     SetFolder s telecom; then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 250 | else | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 252 | error_name="$(dbus_error_name "$TELECOM_OUT")" | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 254 | exit 1 | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 258 | if call_to_file "$MSG_OUT"     org.bluez.obex "$SESSION_PATH" org.bluez.obex.MessageAccess1     SetFolder s msg; then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 260 | else | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 262 | error_name="$(dbus_error_name "$MSG_OUT")" | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 264 | exit 1 | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 268 | if call_to_file "$MESSAGES_OUT"     org.bluez.obex "$SESSION_PATH" org.bluez.obex.MessageAccess1     ListMessages 'sa{sv}' inbox 2 MaxCount q 1 Fields as 1 type; then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 270 | count="$(array_count "$MESSAGES_OUT" 'a{oa{sv}}')" | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 271 | if [[ "$count" == "unknown" ]]; then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 273 | elif (( count > 0 )); then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 275 | else | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 278 | else | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 280 | error_name="$(dbus_error_name "$MESSAGES_OUT")" | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 282 | exit 1 | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 286 | exit 0 | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 290 | if call_to_file "$SELECT_OUT"   org.bluez.obex "$SESSION_PATH" org.bluez.obex.PhonebookAccess1   Select ss int pb; then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 292 | else | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 294 | error_name="$(dbus_error_name "$SELECT_OUT")" | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 296 | exit 1 | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 300 | if call_to_file "$SIZE_OUT"   org.bluez.obex "$SESSION_PATH" org.bluez.obex.PhonebookAccess1 GetSize; then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 302 | size="$(awk 'NR == 1 && $1 == "q" && $2 ~ /^(0\|[1-9][0-9]*)$/ && length($2) <= 5 && $2 + 0 <= 65535 { print $2 }' "$SIZE_OUT")" | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 303 | if [[ -z "$size" ]]; then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 305 | elif (( size > 0 )); then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 307 | else | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 310 | else | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 312 | error_name="$(dbus_error_name "$SIZE_OUT")" | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 314 | exit 1 | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 318 | if call_to_file "$LIST_OUT"   org.bluez.obex "$SESSION_PATH" org.bluez.obex.PhonebookAccess1   List 'a{sv}' 1 MaxCount q 1; then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 320 | count="$(array_count "$LIST_OUT" 'a(ss)')" | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 321 | if [[ "$count" == "unknown" ]]; then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 323 | elif (( count > 0 )); then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 325 | else | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 328 | else | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 330 | error_name="$(dbus_error_name "$LIST_OUT")" | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 332 | exit 1 | test_obex_contract, test_probe_parameters, test_remaining_contracts |

## scripts/probe-obex-session.sh

Assertion families: [test_obex_contract](../scripts/tests/test_obex_contract.py), [test_probe_parameters](../scripts/tests/test_probe_parameters.py), [test_remaining_contracts](../scripts/tests/test_remaining_contracts.py).

| Source line | Decision / method | Assertion mapping |
| --- | --- | --- |
| 9 | usage() { | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 22 | The probe keeps one obexctl process alive for the full session lifetime, | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 28 | while [[ $# -gt 0 ]]; do | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 29 | case "$1" in | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 31 | [[ $# -ge 2 ]] \|\| { echo "--device requires a Bluetooth address." >&2; exit 2; } | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 36 | [[ $# -ge 2 ]] \|\| { echo "--target requires map or pbap." >&2; exit 2; } | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 42 | exit 0 | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 47 | exit 2 | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 52 | if [[ ! "$DEVICE" =~ ^([[:xdigit:]]{2}:){5}[[:xdigit:]]{2}$ ]]; then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 54 | exit 2 | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 57 | if [[ ! "$CONNECT_TIMEOUT" =~ ^[1-9][0-9]{0,17}$ ]] \|\| (( CONNECT_TIMEOUT > 922337203685477580 )); then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 59 | exit 2 | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 62 | case "$TARGET" in | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 75 | exit 2 | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 79 | for command in busctl bluetoothctl obexctl stdbuf mktemp; do | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 80 | if ! command -v "$command" >/dev/null 2>&1; then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 82 | exit 1 | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 89 | if ! busctl --user list 2>/dev/null \| awk '{print $1}' \| grep -Fxq org.bluez.obex; then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 92 | exit 1 | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 96 | if ! bluetoothctl info "$DEVICE" 2>/dev/null \| grep -Eq '^[[:space:]]*Paired:[[:space:]]+yes$'; then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 99 | exit 1 | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 103 | TMP_DIR="$(mktemp -d)" | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 111 | cleanup() { | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 113 | trap - EXIT INT TERM | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 114 | trap '' PIPE | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 116 | if [[ -n "$OBEX_FD" ]]; then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 117 | printf 'disconnect\nquit\n' >&"$OBEX_FD" 2>/dev/null \|\| true | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 118 | exec {OBEX_FD}>&- 2>/dev/null \|\| true | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 121 | if [[ -n "$OBEX_PID" ]] && kill -0 "$OBEX_PID" 2>/dev/null; then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 122 | for _ in 1 2 3 4 5; do | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 123 | kill -0 "$OBEX_PID" 2>/dev/null \|\| break | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 126 | kill "$OBEX_PID" 2>/dev/null \|\| true | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 127 | wait "$OBEX_PID" 2>/dev/null \|\| true | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 131 | exit "$status" | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 133 | trap cleanup EXIT | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 134 | trap 'exit 130' INT | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 135 | trap 'exit 143' TERM | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 143 | wait_for_log() { | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 148 | while (( elapsed < timeout_seconds * 10 )); do | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 149 | if grep -Eq "$pattern" "$OBEX_LOG" 2>/dev/null; then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 150 | return 0 | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 152 | if ! kill -0 "$OBEX_PID" 2>/dev/null; then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 153 | return 1 | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 159 | return 1 | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 162 | if ! wait_for_log 'Client .*/org/bluez/obex\|\[NEW\].*Client' 5; then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 165 | exit 1 | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 171 | if ! wait_for_log 'Connection successful\|Failed to connect' "$CONNECT_TIMEOUT"; then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 173 | echo "error=OBEX connection timed out waiting for phone authorization" | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 174 | exit 1 | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 177 | if grep -Fq 'Failed to connect' "$OBEX_LOG"; then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 180 | exit 1 | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 183 | SESSION_PATH="$( | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 188 | if [[ -z "$SESSION_PATH" ]]; then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 191 | exit 1 | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 196 | if busctl --user introspect   org.bluez.obex   "$SESSION_PATH"   org.bluez.obex.Session1 >/dev/null 2>&1; then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 198 | else | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 200 | exit 1 | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 204 | TARGET_PROPERTY="$( | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 210 | if [[ $TARGET_STATUS -eq 0 ]]; then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 211 | SESSION_TARGET_UUID="$( | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 215 | if [[ ! "$SESSION_TARGET_UUID" =~ ^[[:xdigit:]]{8}-[[:xdigit:]]{4}-[[:xdigit:]]{4}-[[:xdigit:]]{4}-[[:xdigit:]]{12}$ ]]; then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 219 | if [[ "$SESSION_TARGET_UUID" == "$EXPECTED_TARGET_UUID" ]]; then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 221 | else | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 224 | else | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 229 | if busctl --user introspect   org.bluez.obex   "$SESSION_PATH"   "$EXPECTED_INTERFACE" >/dev/null 2>&1; then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 231 | else | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 235 | if wait_for_log "\[NEW\].*$EXPECTED_PROXY_LABEL\|$EXPECTED_PROXY_LABEL /org/bluez/obex/client/session" 2; then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 237 | else | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 241 | if busctl --user introspect   org.bluez.obex   "$SESSION_PATH"   "$EXPECTED_INTERFACE" >/dev/null 2>&1; then | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 244 | else | test_obex_contract, test_probe_parameters, test_remaining_contracts |
| 247 | exit 1 | test_obex_contract, test_probe_parameters, test_remaining_contracts |

## scripts/probe_call_audio_watch.py

Assertion families: [test_watcher_contract](../scripts/tests/test_watcher_contract.py), [test_call_audio_watch](../scripts/tests/test_call_audio_watch.py), [test_watcher_entry](../scripts/tests/test_watcher_entry.py), [test_getcalls_compatibility](../scripts/tests/test_getcalls_compatibility.py), [test_hfp_node_classification](../scripts/tests/test_hfp_node_classification.py).

| Source line | Decision / method | Assertion mapping |
| --- | --- | --- |
| 18 | def command(args): | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 24 | return None | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 25 | return result.stdout if result.returncode == 0 else None | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 28 | def parse_wpctl_id(output): | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 29 | if not isinstance(output, str): | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 30 | return None | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 32 | if not match: | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 33 | return None | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 35 | return value if value <= MAX_NODE_ID else None | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 38 | def parse_sink_mute(output): | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 39 | if not isinstance(output, str) or not re.fullmatch( | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 41 | return "unknown" | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 42 | return "yes" if "[MUTED]" in output else "no" | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 45 | def is_bluetooth(props): | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 46 | return bool(props.get("api.bluez5.address") | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 51 | def graph_snapshot(objects, sink_id, source_id, sink_muted, call_present): | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 55 | for obj in objects: | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 56 | if not isinstance(obj, dict): | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 59 | if info is None: | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 61 | if not isinstance(info, dict) or (info.get("props") is not None | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 64 | if obj.get("type") == "PipeWire:Interface:Node": | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 66 | if type(identifier) is int and 0 <= identifier <= MAX_NODE_ID: | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 68 | elif obj.get("type") == "PipeWire:Interface:Link": | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 69 | if all(type(info.get(key)) is int for key in | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 73 | def props(nid): | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 74 | return (nodes.get(nid) or {}).get("props") or {} | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 76 | outputs = {nid: info for nid, info in nodes.items() | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 77 | if str((info.get("props") or {}).get("media.class") or "") | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 79 | connected_outputs = {link.get("output-node-id") for link in links | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 80 | if link.get("input-node-id") == sink_id | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 83 | bt_nodes = [info for info in nodes.values() | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 84 | if is_bluetooth(info.get("props") or {})] | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 85 | hfp_nodes = [info for info in bt_nodes if is_hfp(info.get("props") or {})] | test_hfp_node_classification |
| 87 | if sink_state not in ("running", "idle", "suspended", "error"): | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 89 | return { | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 91 | "default_sink_present": "yes" if sink_id in nodes else "no", | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 92 | "default_sink_is_bluetooth": "yes" if is_bluetooth(props(sink_id)) else "no", | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 95 | "default_source_present": "yes" if source_id in nodes else "no", | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 96 | "default_source_is_bluetooth": "yes" if is_bluetooth(props(source_id)) else "no", | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 99 | for i in outputs.values()), | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 101 | for i in outputs.values()), | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 108 | def find_gateway(): | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 112 | return gateways[0] if len(gateways) == 1 else None | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 115 | def call_present(gateway): | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 116 | if gateway is None: | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 117 | return "unknown" | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 120 | if output is None: | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 121 | return "unknown" | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 123 | if re.fullmatch(signature + r' 0\s*', output): | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 124 | return "no" | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 127 | if match and int(match.group(1)) <= MAX_NODE_ID: | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 128 | return "yes" | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 129 | return "unknown" | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 132 | def sample(gateway): | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 134 | if raw is None: | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 135 | return None | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 139 | return None | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 140 | if not isinstance(objects, list): | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 141 | return None | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 145 | return graph_snapshot(objects, sink, source, muted, call_present(gateway)), sink, source | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 148 | def emit(index, elapsed, state, first_sink, sink, first_source, source): | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 151 | print("default_sink_changed=" + ("yes" if sink != first_sink else "no"), flush=True) | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 152 | print("default_source_changed=" + ("yes" if source != first_source else "no"), flush=True) | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 153 | for name, value in state.items(): | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 158 | def main(): | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 163 | if not (5 <= args.seconds <= 90) or not (250 <= args.interval_ms <= 2000): | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 165 | if not all(shutil.which(cmd) for cmd in ("pw-dump", "wpctl", "busctl")): | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 168 | return 1 | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 175 | print("telephony_gateway_resolved=" + ("yes" if gateway else "no")) | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 182 | while time.monotonic() - start < args.seconds: | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 184 | if result is None: | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 186 | else: | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 188 | if count == 0: | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 199 | if comparison != previous: | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 207 | return 130 | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 211 | print("call_observed=" + ("yes" if call_seen else "no")) | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 212 | print("sink_muted_at_any_time=" + ("yes" if mute_seen else "no")) | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 213 | print("default_sink_changed_at_any_time=" + ("yes" if sink_changed else "no")) | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 214 | print("hfp_nodes_observed=" + ("yes" if hfp_seen else "no")) | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 216 | ("yes" if stream_disruption else "no")) | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 217 | print("probe_complete=" + ("yes" if count else "no")) | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 219 | return 0 if count else 1 | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |
| 222 | if __name__ == "__main__": | test_watcher_contract, test_call_audio_watch, test_watcher_entry, test_getcalls_compatibility |

## scripts/probe_audio_graph.py

Assertion families: [test_audio_graph](../scripts/tests/test_audio_graph.py), [test_audio_diagnostics_contract](../scripts/tests/test_audio_diagnostics_contract.py), [test_hfp_contract_extended](../scripts/tests/test_hfp_contract_extended.py), [test_hfp_node_classification](../scripts/tests/test_hfp_node_classification.py).

| Source line | Decision / method | Assertion mapping |
| --- | --- | --- |
| 1 | """Shared strict node decoding for read-only feasibility audio classifiers.""" | test_audio_graph, test_audio_diagnostics_contract, test_hfp_contract_extended |
| 5 | def is_hfp(props): | test_hfp_node_classification |
| 7 | return props.get("api.bluez5.profile") in ( | test_hfp_node_classification |
| 11 | def hfp_direction(props): | test_hfp_node_classification |
| 13 | if not is_hfp(props): | test_hfp_node_classification |
| 14 | return None | test_hfp_node_classification |
| 16 | if media == "Audio/Source": | test_hfp_node_classification |
| 17 | return "source" | test_hfp_node_classification |
| 18 | if media == "Audio/Sink": | test_hfp_node_classification |
| 19 | return "sink" | test_hfp_node_classification |
| 20 | if props.get("api.bluez5.profile") == "headset-audio-gateway": | test_hfp_node_classification |
| 21 | if media == "Stream/Output/Audio": | test_hfp_node_classification |
| 22 | return "source" | test_hfp_node_classification |
| 23 | if media == "Stream/Input/Audio": | test_hfp_node_classification |
| 24 | return "sink" | test_hfp_node_classification |
| 25 | return None | test_hfp_node_classification |
| 28 | def valid_nodes(data): | test_audio_graph, test_audio_diagnostics_contract, test_hfp_contract_extended |
| 30 | if not isinstance(data, list): | test_audio_graph, test_audio_diagnostics_contract, test_hfp_contract_extended |
| 33 | for obj in data: | test_audio_graph, test_audio_diagnostics_contract, test_hfp_contract_extended |
| 34 | if not isinstance(obj, dict) or obj.get("type") != "PipeWire:Interface:Node": | test_audio_graph, test_audio_diagnostics_contract, test_hfp_contract_extended |
| 37 | if type(identifier) is not int or not 0 <= identifier <= 4294967295: | test_audio_graph, test_audio_diagnostics_contract, test_hfp_contract_extended |
| 40 | if info is None: | test_audio_graph, test_audio_diagnostics_contract, test_hfp_contract_extended |
| 42 | if not isinstance(info, dict): | test_audio_graph, test_audio_diagnostics_contract, test_hfp_contract_extended |
| 45 | if props is None: | test_audio_graph, test_audio_diagnostics_contract, test_hfp_contract_extended |
| 47 | if not isinstance(props, dict): | test_audio_graph, test_audio_diagnostics_contract, test_hfp_contract_extended |
| 51 | return list(nodes.values()) | test_audio_graph, test_audio_diagnostics_contract, test_hfp_contract_extended |
| 54 | def load_nodes(path): | test_audio_graph, test_audio_diagnostics_contract, test_hfp_contract_extended |
| 57 | return valid_nodes(json.load(handle)) | test_audio_graph, test_audio_diagnostics_contract, test_hfp_contract_extended |

## scripts/probe_obex_monitor.py

Assertion families: [test_obex_monitor](../scripts/tests/test_obex_monitor.py), [test_map_events_contract](../scripts/tests/test_map_events_contract.py), [test_map_send_contract](../scripts/tests/test_map_send_contract.py).

| Source line | Decision / method | Assertion mapping |
| --- | --- | --- |
| 10 | def transfer_status(text, path): | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 12 | if not TRANSFER.fullmatch(path): | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 13 | return "unknown" | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 15 | for block in re.split(r"(?m)^\s*(?=(?:‣\s*)?Type=)", text): | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 16 | if not re.search(r"\bType=signal\b", block): | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 18 | if not re.search(r"\bPath=" + re.escape(path) + r"(?=\s\|$)", block): | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 20 | if not re.search(r"\bInterface=org\.freedesktop\.DBus\.Properties(?=\s\|$)", block): | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 22 | if not re.search(r"\bMember=PropertiesChanged(?=\s\|$)", block): | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 24 | if not re.search(r'STRING "org\.bluez\.obex\.Transfer1";', block): | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 27 | if "error" in statuses: | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 28 | return "error" | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 30 | return "complete" if complete else "unknown" | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 33 | def registration(text, session): | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 34 | """Return registration transfer presence/status for this owned session.""" | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 35 | if not SESSION.fullmatch(session): | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 36 | return "no not_seen" | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 38 | for block in re.split(r"(?m)^\s*(?=(?:‣\s*)?Type=)", text): | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 39 | if not re.search(r"\bType=signal\b", block): | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 45 | if not (changed or added): | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 47 | if 'STRING "org.bluez.obex.Transfer1";' not in block: | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 50 | if not paths: | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 51 | return "no not_seen" | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 52 | statuses = {transfer_status(text, path) for path in paths} | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 53 | return "yes " + ("error" if "error" in statuses else "complete" if "complete" in statuses else "unknown") | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 56 | def message_count(text, session, obexctl=False): | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 58 | if not SESSION.fullmatch(session): | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 59 | return 0 | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 63 | if obexctl: | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 65 | else: | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 67 | for block in re.split(r"(?m)^\s*(?=(?:‣\s*)?Type=)", text): | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 68 | if not re.search(r"\bType=signal\b", block) or 'STRING "org.bluez.obex.Message1";' not in block: | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 70 | if not re.search(r"\bInterface=org\.freedesktop\.DBus\.ObjectManager(?=\s\|$)", block): | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 73 | if not member: | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 75 | for path in re.findall(r'OBJECT_PATH "(' + pattern + r')";', block): | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 76 | events.append(("NEW" if member[1] == "Added" else "DEL", path)) | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 77 | for kind, path in events: | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 78 | if kind == "DEL": | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 80 | elif path not in active: | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 83 | return count | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 86 | def main(argv=None): | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 87 | args = sys.argv[1:] if argv is None else argv | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 89 | if args and args[0] in ("--messages", "--obex-messages", "--registration"): | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 91 | if len(args) != 2: | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 93 | return 2 | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 99 | return 1 | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 100 | if mode == "--registration": | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 102 | elif mode in ("--messages", "--obex-messages"): | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 104 | else: | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 106 | return 0 | test_obex_monitor, test_map_events_contract, test_map_send_contract |
| 109 | if __name__ == "__main__": | test_obex_monitor, test_map_events_contract, test_map_send_contract |

## crates/nativepair-core/src/lib.rs

Assertion families: Rust exhaustive_contract_tests.

| Source line | Decision / method | Assertion mapping |
| --- | --- | --- |
| 53 | pub fn new(platform: PhonePlatform) -> Self { | exhaustive_contract_tests |
| 61 | pub const fn platform(&self) -> PhonePlatform { | exhaustive_contract_tests |
| 66 | pub fn availability(&self, capability: Capability) -> Availability { | exhaustive_contract_tests |
| 73 | pub fn set_availability( | exhaustive_contract_tests |
| 84 | pub fn supports(&self, capability: Capability) -> bool { | exhaustive_contract_tests |

## crates/nativepair-cli/src/main.rs

Assertion families: [test_binary_contract](../scripts/tests/test_binary_contract.py).

| Source line | Decision / method | Assertion mapping |
| --- | --- | --- |
| 18 | fn main() -> ExitCode { | test_binary_contract |
| 22 | Some("--version" \| "-V") if args.next().is_none() => { | test_binary_contract |
| 26 | Some("--help" \| "-h") if args.next().is_none() => { | test_binary_contract |

## crates/nativepair-daemon/src/main.rs

Assertion families: [test_binary_contract](../scripts/tests/test_binary_contract.py).

| Source line | Decision / method | Assertion mapping |
| --- | --- | --- |
| 9 | fn main() -> ExitCode { | test_binary_contract |
| 13 | Some("--version" \| "-V") if args.next().is_none() => { | test_binary_contract |
