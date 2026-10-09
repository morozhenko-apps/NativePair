"""Thin observer entry point: forwarding and process exit contracts."""
import unittest

from scenarios import add_cases
from probe_harness import REPO, assert_safe, route, run_probe


class WatcherEntryContracts(unittest.TestCase):
    pass


def check(self, value):
    args, code, missing = value
    result = run_probe("probe-call-audio-watch.sh", args=args, missing=missing,
                       routes=[route("python3", stdout="wrapper_fixture=yes\n", exit=code)])
    assert_safe(self, result, code)
    if missing:
        self.assertEqual(result.state["commands"], [])
    else:
        self.assertEqual(result.stdout, "wrapper_fixture=yes\n")
        self.assertEqual(result.state["commands"], [["python3", str(REPO / "scripts/probe_call_audio_watch.py"), *args]])


add_cases(WatcherEntryContracts, "Positive", "arguments_forwarded", [
    ("none", ((), 0, ())),
    ("multiple", (("--seconds", "5", "--interval-ms", "250"), 0, ())),
    ("quoted_empty_value", (("--seconds", "", "two words"), 0, ())),
], check)
add_cases(WatcherEntryContracts, "N3", "python_failure_propagated", [
    ("usage_error", (("--unknown",), 2, ())),
    ("runtime_error", ((), 1, ())),
], check)
add_cases(WatcherEntryContracts, "N9", "interrupt_exit_propagated", [
    ("interrupted", ((), 130, ())),
], check)
add_cases(WatcherEntryContracts, "N7", "python_missing", [
    ("missing_executable", ((), 127, ("python3",))),
], check)


def actual_entry(self, args):
    result = run_probe("probe-call-audio-watch.sh", args=args)
    expected = 0 if args == ("--help",) else 2
    assert_safe(self, result, expected)
    self.assertEqual(result.state["commands"], [])
    self.assertNotIn("nativepair_call_audio_watch_schema", result.stdout)


add_cases(WatcherEntryContracts, "Positive", "actual_python_entry_help", [
    ("help", ("--help",)),
], actual_entry)
add_cases(WatcherEntryContracts, "N1", "actual_python_entry_rejected", [
    ("seconds_below_limit", ("--seconds", "4")),
    ("unknown_argument", ("--unknown",)),
], actual_entry)
