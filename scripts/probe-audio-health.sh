#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C

ITERATIONS="${NATIVEPAIR_AUDIO_HEALTH_ITERATIONS:-10}"
RECENT_WINDOW="${NATIVEPAIR_AUDIO_HEALTH_JOURNAL_WINDOW:-2 minutes}"

if [[ ! "$ITERATIONS" =~ ^[0-9]+$ ]] || (( ITERATIONS < 2 || ITERATIONS > 60 )); then
  echo "NATIVEPAIR_AUDIO_HEALTH_ITERATIONS must be an integer from 2 to 60." >&2
  exit 2
fi

for command in grep journalctl mktemp python3 pw-top systemctl timeout; do
  if ! command -v "$command" >/dev/null 2>&1; then
    echo "Required command is missing: $command" >&2
    exit 1
  fi
done

TMP_DIR="$(mktemp -d)"
PW_TOP_RAW="$TMP_DIR/pw-top.raw"
PW_TOP_RESULT="$TMP_DIR/pw-top.result"
PIPEWIRE_LOG="$TMP_DIR/pipewire.log"
WIREPLUMBER_LOG="$TMP_DIR/wireplumber.log"

cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT INT TERM

echo "nativepair_audio_health_probe_schema=1"
echo "personal_payload_printed=no"
echo "audio_configuration_changed=no"
echo "observation_iterations=$ITERATIONS"

if systemctl --user is-active --quiet pipewire.service 2>/dev/null; then
  echo "pipewire_service_active=yes"
else
  echo "pipewire_service_active=no"
fi

if systemctl --user is-active --quiet wireplumber.service 2>/dev/null; then
  echo "wireplumber_service_active=yes"
else
  echo "wireplumber_service_active=no"
fi

set +e
timeout "$((ITERATIONS + 8))s" pw-top -b -n "$ITERATIONS" >"$PW_TOP_RAW" 2>/dev/null
PW_TOP_STATUS=$?
set -e

if [[ $PW_TOP_STATUS -ne 0 ]]; then
  echo "pw_top_capture_succeeded=no"
  echo "pw_top_exit_status=$PW_TOP_STATUS"
  exit 1
fi
echo "pw_top_capture_succeeded=yes"

python3 - "$PW_TOP_RAW" >"$PW_TOP_RESULT" <<'PY'
import collections
import sys

path = sys.argv[1]
first_err = {}
last_err = {}
max_err = {}
seen_ids = set()
snapshots = 0
rows = 0
running_rows = 0
error_state_rows = 0
nonzero_pairs = set()

with open(path, "r", encoding="utf-8", errors="replace") as handle:
    for raw in handle:
        line = raw.strip()
        if not line:
            continue
        if line.startswith("S   ID  QUANT"):
            snapshots += 1
            continue

        parts = line.split()
        if len(parts) < 9:
            continue

        state = parts[0]
        node_id = parts[1]
        quant = parts[2]
        rate = parts[3]
        err = parts[8]

        if state not in {"E", "C", "S", "I", "R", "t", "T", "!"}:
            continue
        if not node_id.isdigit() or not err.isdigit():
            continue

        rows += 1
        if state in {"R", "t", "T"}:
            running_rows += 1
        if state == "E":
            error_state_rows += 1

        nid = int(node_id)
        value = int(err)
        seen_ids.add(nid)
        first_err.setdefault(nid, value)
        last_err[nid] = value
        max_err[nid] = max(max_err.get(nid, value), value)

        if quant.isdigit() and rate.isdigit():
            q = int(quant)
            r = int(rate)
            if q > 0 and r > 0:
                nonzero_pairs.add((q, r))

growth = {}
for nid in seen_ids:
    delta = max_err.get(nid, 0) - first_err.get(nid, 0)
    if delta > 0:
        growth[nid] = delta

positive_now = sum(1 for value in last_err.values() if value > 0)
max_delta = max(growth.values(), default=0)
max_value = max(last_err.values(), default=0)

print(f"pw_top_snapshots={snapshots}")
print(f"pw_top_rows_parsed={rows}")
print(f"running_rows_observed={running_rows}")
print(f"error_state_rows_observed={error_state_rows}")
print(f"nodes_with_nonzero_err_at_end={positive_now}")
print(f"nodes_with_err_growth={len(growth)}")
print(f"max_single_node_err_delta={max_delta}")
print(f"max_err_value_at_end={max_value}")
print(f"xrun_or_error_growth_observed={'yes' if growth else 'no'}")
print(f"nonzero_quantum_rate_pair_count={len(nonzero_pairs)}")
PY

cat "$PW_TOP_RESULT"

journalctl --user -u pipewire.service --since "-$RECENT_WINDOW" -p warning   --no-pager --output=cat >"$PIPEWIRE_LOG" 2>/dev/null || true
journalctl --user -u wireplumber.service --since "-$RECENT_WINDOW" -p warning   --no-pager --output=cat >"$WIREPLUMBER_LOG" 2>/dev/null || true

PIPEWIRE_WARNINGS="$(grep -cve '^[[:space:]]*$' "$PIPEWIRE_LOG" || true)"
WIREPLUMBER_WARNINGS="$(grep -cve '^[[:space:]]*$' "$WIREPLUMBER_LOG" || true)"

printf 'recent_pipewire_warning_lines=%s\n' "$PIPEWIRE_WARNINGS"
printf 'recent_wireplumber_warning_lines=%s\n' "$WIREPLUMBER_WARNINGS"

if grep -Eqi 'xrun|underrun|overrun|deadline|missed' "$PIPEWIRE_LOG" "$WIREPLUMBER_LOG"; then
  echo "recent_audio_deadline_keywords=yes"
else
  echo "recent_audio_deadline_keywords=no"
fi

if grep -Eqi 'bluez|bluetooth|sco|hfp|transport' "$PIPEWIRE_LOG" "$WIREPLUMBER_LOG"; then
  echo "recent_bluetooth_audio_warning_keywords=yes"
else
  echo "recent_bluetooth_audio_warning_keywords=no"
fi

echo "probe_complete=yes"
echo "note=read_only_health_window_no_names_or_raw_logs_printed"
