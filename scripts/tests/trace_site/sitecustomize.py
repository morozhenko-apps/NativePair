"""Opt-in, test-only source tracing without command values or private data."""
import atexit
import json
import os
from pathlib import Path
import sys

destination = os.environ.get("NATIVEPAIR_PYTHON_TRACE")
if destination:
    root = Path(os.environ["NATIVEPAIR_TRACE_ROOT"]).resolve()
    allowed = {str(path) for path in (root / "scripts").glob("probe*.py")}
    script = os.environ.get("NATIVEPAIR_TRACE_SCRIPT")
    lines = set()
    arcs = set()
    previous = {}

    def trace(frame, event, arg):
        filename = frame.f_code.co_filename
        if filename not in allowed and not (filename == "<stdin>" and script):
            return None
        name = filename if filename != "<stdin>" else script + "::python"
        identity = id(frame)
        if event == "line":
            lines.add((name, frame.f_lineno))
            if identity in previous:
                arcs.add((name, previous[identity], frame.f_lineno))
            previous[identity] = frame.f_lineno
        elif event == "return":
            previous.pop(identity, None)
        return trace

    def save():
        target = Path(destination)
        target.mkdir(parents=True, exist_ok=True)
        (target / f"{os.getpid()}.json").write_text(json.dumps({"lines": sorted(lines), "arcs": sorted(arcs)}))

    atexit.register(save)
    sys.settrace(trace)
