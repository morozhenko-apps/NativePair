"""Run production Bash probes with an allowlisted PATH and owned processes."""
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
from types import SimpleNamespace

REPO = Path(__file__).resolve().parents[2]
DEVICE = "02:00:00:00:00:01"
SECRET = "PRIVATE_CONTACT"
NUMBER = "+15551234567"
EXTERNALS = ("bluetoothctl", "busctl", "obexctl", "systemctl", "journalctl",
             "pw-dump", "wpctl", "pw-top", "pipewire", "wireplumber", "sdptool",
             "dpkg-query", "pgrep", "strings")
TOOLS = ("bash", "python3", "env", "cat", "grep", "awk", "sed", "head", "tail", "tr",
         "mktemp", "mkfifo", "stdbuf", "wc", "od", "chmod", "rm", "seq", "timeout",
         "dirname", "readlink", "mkdir", "install", "sha256sum", "dpkg-deb", "dpkg",
         "du", "touch", "find", "basename", "test")


def route(command, match=".*", stdout="", exit=0, **extra):
    return {"command": command, "match": match, "stdout": stdout, "exit": exit, **extra}


def run_probe(script, args=(), env=None, routes=(), config=None, missing=()):
    with tempfile.TemporaryDirectory(prefix="nativepair-contract-") as temporary:
        root = Path(temporary)
        binary = root / "bin"
        binary.mkdir()
        (root / "tmp").mkdir()
        cfg = {"routes": list(routes), **(config or {})}
        obex_process = None
        if "mns_flags" in cfg:
            obex_process = subprocess.Popen(
                [sys.executable, "-c", "import signal; signal.pause()", *cfg.pop("mns_flags")],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            cfg["obex_pid"] = obex_process.pid
        wrapped = set(EXTERNALS) | {rule["command"] for rule in routes}
        if cfg.get("capture_payload"):
            wrapped.add("chmod")
        cfg["real_tools"] = {}
        for name in TOOLS:
            actual = shutil.which(name)
            if actual is None:
                raise RuntimeError(f"Test prerequisite missing: {name}")
            if name in wrapped:
                cfg["real_tools"][name] = actual
            else:
                (binary / name).symlink_to(actual)
        for name in wrapped:
            (binary / name).symlink_to(REPO / "scripts/tests/fake_system.py")
        # Fake adapters flush explicitly; do not preload a host stdbuf library
        # into Python or create uutils stdbuf's unrelated temporary directory.
        if "stdbuf" not in wrapped:
            (binary / "stdbuf").unlink()
            (binary / "stdbuf").write_text('#!/bin/sh\nshift\nshift\nexec "$@"\n')
            (binary / "stdbuf").chmod(0o755)
        if "sleep" not in wrapped:
            (binary / "sleep").write_text("#!/bin/sh\nexit 0\n")
            (binary / "sleep").chmod(0o755)
        for name in missing:
            (binary / name).unlink(missing_ok=True)
        initial = {"commands": [], "route_counts": {}, "call_exists": False,
                   "transport": "idle", **cfg.pop("initial", {})}
        (root / "state.json").write_text(json.dumps(initial))
        (root / "config.json").write_text(json.dumps(cfg))
        environment = {
            "PATH": str(binary), "TMPDIR": str(root / "tmp"),
            "HOME": str(root), "LC_ALL": "C", "NATIVEPAIR_TEST_ROOT": str(root),
            "NATIVEPAIR_DEVICE": DEVICE, "NATIVEPAIR_SMS_RECIPIENT": NUMBER,
            "NATIVEPAIR_CALL_RECIPIENT": NUMBER,
            "NATIVEPAIR_OBEX_TIMEOUT": "1", "NATIVEPAIR_SEND_TIMEOUT": "1",
            "NATIVEPAIR_EVENT_TIMEOUT": "1", "NATIVEPAIR_HFP_CONNECT_TIMEOUT": "1",
            "NATIVEPAIR_SCO_STATE_TIMEOUT": "1", "NATIVEPAIR_CALL_ACTIVE_TIMEOUT": "1",
            "NATIVEPAIR_SCO_HUMAN_WINDOW": "1", "NATIVEPAIR_CALL_OBSERVE_SECONDS": "1",
            **(env or {}),
        }
        trace_path = os.environ.get("NATIVEPAIR_TEST_TRACE")
        if trace_path:
            trace_environment = root / "trace.bash"
            trace_environment.write_text('set -o functrace\n'
                'trap \'printf "%s:%s\\n" "${BASH_SOURCE[0]}" "$LINENO" >> "$NATIVEPAIR_TEST_TRACE"\' DEBUG\n')
            environment.update(BASH_ENV=str(trace_environment), NATIVEPAIR_TEST_TRACE=trace_path)
        for key in ("PYTHONPATH", "COVERAGE_PROCESS_START", "NATIVEPAIR_PYTHON_TRACE", "NATIVEPAIR_TRACE_ROOT"):
            if key in os.environ:
                environment[key] = os.environ[key]
        if "NATIVEPAIR_PYTHON_TRACE" in environment:
            environment["NATIVEPAIR_TRACE_SCRIPT"] = str(REPO / "scripts" / script)
        # The process group is created and owned by this exact test invocation.
        process = subprocess.Popen([str(binary / "bash"), "-c",
                                   'printf "%s\\n" "$$" > "$NATIVEPAIR_TEST_ROOT/probe.pid"; exec "$@"',
                                   "probe-launch", str(binary / "bash"), str(REPO / "scripts" / script), *args],
                                   env=environment, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True, start_new_session=True)
        try:
            stdout, stderr = process.communicate(timeout=20)
        finally:
            # Also reap an adapter orphaned by a production cleanup defect.
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
            if obex_process is not None:
                obex_process.terminate()
                obex_process.wait(timeout=5)
        state = json.loads((root / "state.json").read_text())
        return SimpleNamespace(returncode=process.returncode, stdout=stdout, stderr=stderr,
                               state=state, remaining=[p.name for p in (root / "tmp").iterdir()])


def assert_safe(test, result, expected=0, fields=()):
    test.assertEqual(result.returncode, expected, result.stdout + result.stderr)
    for field in fields:
        test.assertIn(field, result.stdout.splitlines())
    for private in (DEVICE, NUMBER, SECRET):
        test.assertNotIn(private, result.stdout + result.stderr)
    test.assertEqual(result.remaining, [], "Probe leaked temporary artifacts")


def commands(result, method):
    return [command for command in result.state["commands"] if method in command]
