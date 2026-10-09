"""Observed PipeWire dictionary wire replies and legacy call-array contracts."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from probe_harness import assert_safe, commands, route, run_probe
from scenarios import add_cases

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import probe_call_audio_watch as watch

SIGNATURES = (("dictionary", "a{oa{sv}}"), ("struct_array", "a(oa{sv})"))
GATEWAY = "/org/pipewire/Telephony/ag0"
SCRIPTS = ("probe-hfp-call.sh", "probe-hfp-sco.sh")


class GetCallsCompatibility(unittest.TestCase):
    pass


def check_guard(self, value):
    script, reply, existing = value
    # Arrange / Act: run the actual no-dial entry point with one wire reply.
    result = run_probe(script, routes=[route("busctl", "GetCalls", reply)])
    # Assert: neither preflight nor a refusal may mutate a call/transport.
    fields = (["preexisting_call_present=yes", "probe_complete=blocked"] if existing
              else ["call_state_query_succeeded=yes", "preexisting_call_present=no", "probe_complete=preflight"])
    assert_safe(self, result, 1 if existing else 0, fields)
    for method in ("Dial", "HangupAll", "Activate"):
        self.assertEqual(commands(result, method), [])


add_cases(GetCallsCompatibility, "Positive", "empty_guard_accepts_wire_signature", [
    (script.replace("-", "_").replace(".", "_") + name + str(index),
     (script, signature + " 0" + whitespace, False))
    for script in SCRIPTS for name, signature in SIGNATURES
    for index, whitespace in enumerate(("", " \n"))], check_guard)

add_cases(GetCallsCompatibility, "N7", "existing_guard_preserves_call", [
    (script.replace("-", "_").replace(".", "_") + name,
     (script, signature + f' 1 "{GATEWAY}/call0" 0', True))
    for script in SCRIPTS for name, signature in SIGNATURES], check_guard)


def check_lifecycle(self, value):
    script, signature = value
    # Arrange: the same wire form appears before and after the owned Dial.
    active = signature + f' 1 "{GATEWAY}/call0" 1 "State" s "active"'
    reply = route("busctl", "GetCalls", replies=[
        {"stdout": signature + " 0"}, {"stdout": active}])
    # Act.
    result = run_probe(script, args=("--dial",), routes=[reply])
    # Assert.
    assert_safe(self, result, 0, ["call_state_query_succeeded=yes", "preexisting_call_present=no"])
    self.assertEqual(len(commands(result, "Dial")), 1)
    self.assertEqual(len(commands(result, "HangupAll")), 1)
    self.assertEqual(len(commands(result, "Activate")), int(script == "probe-hfp-sco.sh"))
    self.assertFalse(result.state["call_exists"])


add_cases(GetCallsCompatibility, "Positive", "owned_call_uses_wire_signature", [
    (script.replace("-", "_").replace(".", "_") + name, (script, signature))
    for script in SCRIPTS for name, signature in SIGNATURES], check_lifecycle)


def check_bad_empty(self, value):
    script, reply = value
    # Arrange / Act: even --dial must stop at an unproven empty call set.
    result = run_probe(script, args=("--dial",), routes=[route("busctl", "GetCalls", reply)])
    # Assert.
    assert_safe(self, result, 1, ["call_state_query_succeeded=no"])
    for method in ("Dial", "HangupAll", "Activate"):
        self.assertEqual(commands(result, method), [])


add_cases(GetCallsCompatibility, "N6", "malformed_empty_reply_blocks_dial", [
    (script.replace("-", "_").replace(".", "_") + name + str(index), (script, signature + suffix))
    for script in SCRIPTS for name, signature in SIGNATURES
    for index, suffix in enumerate((" 00", " 01", " -1", " 4294967296", "", " PRIVATE_CONTACT"))], check_bad_empty)


def check_observer(self, value):
    consumer, reply, expected = value
    # Arrange / Act: only external I/O is replaced, never the call parser.
    if consumer == "watcher":
        with patch.object(watch, "command", return_value=reply):
            actual = watch.call_present(GATEWAY)
        # Assert.
        self.assertEqual(actual, expected)
    else:
        result = run_probe("probe-hfp.sh", routes=[route("busctl", "GetCalls", reply)])
        assert_safe(self, result, 0, ["call_objects_present=" + expected])
        for method in ("Dial", "HangupAll", "Activate"):
            self.assertEqual(commands(result, method), [])


add_cases(GetCallsCompatibility, "Positive", "observer_recognizes_wire_signature", [
    (consumer + name + str(index), (consumer, signature + suffix, expected))
    for consumer in ("watcher", "passive") for name, signature in SIGNATURES
    for index, (suffix, expected) in enumerate((
        (" 0", "no"), (" 0 \n", "no"), (f' 1 "{GATEWAY}/call0" 0', "yes")))], check_observer)

add_cases(GetCallsCompatibility, "N6", "observer_rejects_corrupt_wire_reply", [
    (consumer + name + str(index), (consumer, signature + suffix, "unknown"))
    for consumer in ("watcher", "passive") for name, signature in SIGNATURES
    for index, suffix in enumerate((
        " 1", ' 1 "/org/pipewire/Telephony/ag1/call0" 0',
        f' 0 "{GATEWAY}/call0" 0', f' 01 "{GATEWAY}/call0" 0',
        f' 4294967296 "{GATEWAY}/call0" 0', f' 1 "{GATEWAY}/call0private" 0',
        " -1", " PRIVATE_CONTACT"))], check_observer)
