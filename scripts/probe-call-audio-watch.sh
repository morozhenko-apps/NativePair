#!/usr/bin/env bash
set -euo pipefail
exec python3 "$(dirname -- "$0")/probe_call_audio_watch.py" "$@"
