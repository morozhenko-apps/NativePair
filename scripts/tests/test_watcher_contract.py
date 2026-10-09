"""Observer contracts: real parsers/lifecycle, fake external commands and clock."""
import contextlib
import io
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from scenarios import add_cases, category

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import probe_call_audio_watch as watch

GATEWAY = "/org/pipewire/Telephony/ag0"
SECRET = "PRIVATE_CONTACT_+15551234567_02:00:00:00:00:01"


def node(identifier, role="Audio/Sink", state="running", **props):
    return {"id": identifier, "type": "PipeWire:Interface:Node",
            "info": {"state": state, "props": {"media.class": role, **props}}}


def link(out=50, target=41, state="active"):
    return {"type": "PipeWire:Interface:Link", "info": {
        "output-node-id": out, "input-node-id": target, "state": state}}


def empty_snapshot():
    return {"call_present": "unknown", "default_sink_present": "no",
            "default_sink_is_bluetooth": "no", "default_sink_state": "unknown",
            "default_sink_muted": "unknown", "default_source_present": "no",
            "default_source_is_bluetooth": "no", "output_streams": 0,
            "output_streams_running": 0, "output_streams_suspended": 0,
            "direct_output_stream_links_to_sink": 0,
            "bluetooth_nodes": 0, "hfp_nodes": 0}


class WatcherContracts(unittest.TestCase):
    @category("N10")
    def test_given_private_graph_when_snapshot_emitted_then_only_allowlisted_fields_escape(self):
        # Arrange
        objects = [node(41, **{"node.name": SECRET, "api.bluez5.address": SECRET}),
                   node(42, "Audio/Source"), node(50, "Stream/Output/Audio"), link()]
        # Act
        state = watch.graph_snapshot(objects, 41, 42, "yes", "yes")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            watch.emit(1, 1.9, state, 1, 41, 42, 42)
        # Assert
        self.assertEqual(set(state), set(empty_snapshot()))
        self.assertNotIn(SECRET, output.getvalue())
        self.assertIn("elapsed_seconds=1\n", output.getvalue())
        self.assertIn("default_sink_changed=yes\n", output.getvalue())
        self.assertIn("default_source_changed=no\n", output.getvalue())
        self.assertTrue(output.getvalue().endswith("sample_end=yes\n"))


def check_command(self, value):
    exception, code, expected = value
    result = subprocess.CompletedProcess(["fake"], code, SECRET, SECRET)
    output = io.StringIO()
    with patch.object(watch.subprocess, "run", side_effect=exception,
                      return_value=result) as run, contextlib.redirect_stdout(output):
        actual = watch.command(["fake", "read"])
    self.assertEqual(actual, expected)
    run.assert_called_once_with(["fake", "read"], capture_output=True, text=True,
                                timeout=4, check=False)
    self.assertEqual(output.getvalue(), "")


add_cases(WatcherContracts, "Positive", "command_captured", [
    ("successful_subprocess", (None, 0, SECRET))], check_command)
add_cases(WatcherContracts, "N3", "command_failed", [
    ("nonzero_subprocess", (None, 1, None)),
    ("missing_executable", (FileNotFoundError(SECRET), 0, None)),
    ("denied_executable", (PermissionError(SECRET), 0, None)),
    ("timed_out_subprocess", (subprocess.TimeoutExpired("fake", 4, SECRET), 0, None)),
], check_command)


def check_id(self, value):
    text, expected = value
    self.assertEqual(watch.parse_wpctl_id(text), expected)


add_cases(WatcherContracts, "Positive", "id_parsed", [
    ("zero_id", ("id 0, type Node", 0)),
    ("normal_id", ("id 41, type Node", 41)),
    ("multiline_id", ("ignored\nid 42, type Node\n", 42)),
    ("large_id", ("id 4294967295, type Node", 4294967295)),
], check_id)
add_cases(WatcherContracts, "N6", "id_rejected", [
    (name, (value, None)) for name, value in [
        ("null_id", None), ("empty_id", ""), ("negative_id", "id -1,"),
        ("prefix_id", "Xid 41,"), ("missing_comma", "id 41"),
        ("text_id", "id x,"), ("decimal_id", "id 1.5,"),
        ("private_id", SECRET)]], check_id)


def check_mute(self, value):
    text, expected = value
    self.assertEqual(watch.parse_sink_mute(text), expected)


add_cases(WatcherContracts, "Positive", "mute_parsed", [
    ("unmuted_zero", ("Volume: 0.00", "no")),
    ("unmuted_normal", ("Volume: 0.50\n", "no")),
    ("muted", ("Volume: 0.50 [MUTED]\n", "yes")),
    ("amplified", ("Volume: 2.00", "no")),
], check_mute)
add_cases(WatcherContracts, "N6", "mute_rejected", [
    (name, (value, "unknown")) for name, value in [
        ("null_mute", None), ("empty_mute", ""), ("bad_type_mute", 3),
        ("nan_mute", "Volume: NaN"), ("infinite_mute", "Volume: Infinity"),
        ("negative_mute", "Volume: -0.1"), ("missing_volume", "Volume:"),
        ("private_mute", "Volume: " + SECRET),
        ("unknown_suffix", "Volume: 0.50 " + SECRET)]], check_mute)


def check_bluetooth(self, value):
    props, expected = value
    self.assertEqual(watch.is_bluetooth(props), expected)


add_cases(WatcherContracts, "Positive", "bluetooth_classified", [
    ("address", ({"api.bluez5.address": SECRET}, True)),
    ("profile", ({"api.bluez5.profile": "headset-head-unit"}, True)),
    ("device_api", ({"device.api": "bluez5"}, True)),
    ("local_device", ({"device.api": "alsa"}, False)),
    ("empty_properties", ({}, False)),
    ("empty_bt_properties", ({"api.bluez5.address": "", "api.bluez5.profile": None}, False)),
], check_bluetooth)


def check_graph(self, value):
    objects, sink, source, changes = value
    expected = empty_snapshot()
    expected.update(changes)
    self.assertEqual(watch.graph_snapshot(objects, sink, source, "unknown", "unknown"), expected)


graph_cases = [("empty_graph", ([], None, None, {})),
               ("stale_defaults", ([], 41, 42, {}))]
for state in ["running", "idle", "suspended", "error", "unknown", SECRET, None]:
    graph_cases.append(("sink_state_" + str(len(graph_cases)), (
        [node(41, state=state)], 41, None,
        {"default_sink_present": "yes", "default_sink_state":
         state if state in ("running", "idle", "suspended", "error") else "unknown"})))
for role in ["Audio/Sink", "Audio/Source", "Stream/Output/Audio", "Stream/Input/Audio", "Video/Source", None]:
    for state in ["running", "suspended", "idle"]:
        graph_cases.append(("role_state_" + str(len(graph_cases)), (
            [node(50, role, state)], None, None,
            {"output_streams": int(role == "Stream/Output/Audio"),
             "output_streams_running": int(role == "Stream/Output/Audio" and state == "running"),
             "output_streams_suspended": int(role == "Stream/Output/Audio" and state == "suspended")})))
for state in ["active", "paused", "init", "error", "unlinked", None]:
    graph_cases.append(("link_state_" + str(len(graph_cases)), (
        [node(41), node(50, "Stream/Output/Audio"), link(state=state)], 41, None,
        {"default_sink_present": "yes", "default_sink_state": "running",
         "output_streams": 1, "output_streams_running": 1,
         "direct_output_stream_links_to_sink": int(state in ("active", "paused", "init"))})))
for name, links in [
        ("duplicate_links", [link(), link()]),
        ("wrong_sink", [link(target=42)]),
        ("unknown_output", [link(out=51)]),
        ("input_stream_link", [link(out=60)])]:
    graph_cases.append((name, ([node(50, "Stream/Output/Audio"),
                                node(60, "Stream/Input/Audio")] + links,
                               41, None, {"output_streams": 1, "output_streams_running": 1,
                                          "direct_output_stream_links_to_sink": int(name == "duplicate_links")})))
for kind in ["api.bluez5.address", "api.bluez5.profile", "device.api"]:
    props = {kind: "bluez5" if kind == "device.api" else "headset-head-unit"}
    graph_cases.append(("bt_kind_" + kind.replace(".", "_"), (
        [node(41, **props), node(42, "Audio/Source", **props)], 41, 42,
        {"default_sink_present": "yes", "default_source_present": "yes",
         "default_sink_state": "running", "default_sink_is_bluetooth": "yes",
         "default_source_is_bluetooth": "yes", "bluetooth_nodes": 2,
         "hfp_nodes": 2 if kind == "api.bluez5.profile" else 0})))
add_cases(WatcherContracts, "Positive", "graph_classified", graph_cases, check_graph)
add_cases(WatcherContracts, "N6", "corrupt_graph_filtered", [
    ("malformed_object_" + str(i), ([obj], None, None, {}))
    for i, obj in enumerate([
        None, 1, [], "private", {}, {"type": "Other"},
        {"type": "PipeWire:Interface:Node", "id": []},
        {"type": "PipeWire:Interface:Node", "id": True},
        {"type": "PipeWire:Interface:Node", "id": -1},
        {"type": "PipeWire:Interface:Node", "id": 1, "info": SECRET},
        {"type": "PipeWire:Interface:Node", "id": 1, "info": {"props": SECRET}},
        {"type": "PipeWire:Interface:Link", "info": {}},
        {"type": "PipeWire:Interface:Link", "info": {"output-node-id": [], "input-node-id": None}},
    ])], check_graph)


def check_gateway(self, value):
    text, expected = value
    with patch.object(watch, "command", return_value=text) as external:
        self.assertEqual(watch.find_gateway(), expected)
    self.assertEqual(external.call_args.args[0][-1], "GetModems")


add_cases(WatcherContracts, "N6", "gateway_resolved", [
    ("missing_gateway", (None, None)), ("empty_gateways", ("a(oa{sv}) 0", None)),
    ("single_gateway", (f'a(oa{{sv}}) 1 "{GATEWAY}" 0', GATEWAY)),
    ("duplicate_gateway", (f'"{GATEWAY}" "{GATEWAY}"', GATEWAY)),
    ("ambiguous_gateways", (f'"{GATEWAY}" "/org/pipewire/Telephony/ag1"', None)),
    ("call_not_gateway", (f'"{GATEWAY}/call0"', None)),
    ("suffix_not_gateway", (f'"{GATEWAY}private"', None)),
    ("unquoted_gateway", (GATEWAY, None)),
], check_gateway)


def check_call(self, value):
    gateway, text, expected = value
    with patch.object(watch, "command", return_value=text) as external:
        self.assertEqual(watch.call_present(gateway), expected)
    self.assertEqual(external.call_count, int(gateway is not None))


add_cases(WatcherContracts, "N6", "call_observed", [
    ("unknown_gateway", (None, "", "unknown")),
    ("failed_query", (GATEWAY, None, "unknown")),
    ("no_calls", (GATEWAY, "a(oa{sv}) 0", "no")),
    ("one_call", (GATEWAY, f'a(oa{{sv}}) 1 "{GATEWAY}/call0" 0', "yes")),
    ("malformed_calls", (GATEWAY, SECRET, "unknown")),
    ("call_suffix", (GATEWAY, f'a(oa{{sv}}) 1 "{GATEWAY}/call0private" 0', "no")),
], check_call)


def external_responses(raw="[]", sink="id 41,", source="id 42,", muted="Volume: 0.5", calls="a(oa{sv}) 0"):
    def command(args):
        if args == ["pw-dump"]:
            return raw
        if args[0] == "wpctl":
            return muted if args[1] == "get-volume" else sink if "SINK" in args[-1] else source
        return calls
    return command


def check_sample(self, value):
    raw, expected = value
    with patch.object(watch, "command", side_effect=external_responses(raw)):
        actual = watch.sample(None)
    if expected is None:
        self.assertIsNone(actual)
    else:
        state, sink, source = actual
        self.assertEqual((sink, source), (41, 42))
        self.assertEqual(state, expected)


add_cases(WatcherContracts, "N6", "sample_parsed", [
    ("missing_dump", (None, None)), ("broken_json", ("{" + SECRET, None)),
    ("object_dump", ("{}", None)), ("null_dump", ("null", None)),
    ("scalar_dump", ("5", None)), ("string_dump", (json.dumps(SECRET), None)),
    ("corrupt_entries", ('[null,3,"text"]', {**empty_snapshot(), "default_sink_muted": "no"})),
    ("empty_dump", ("[]", {**empty_snapshot(), "default_sink_muted": "no"})),
], check_sample)


class FakeClock:
    def __init__(self, interrupt=False):
        self.value = 0
        self.interrupt = interrupt

    def monotonic(self):
        return self.value

    def sleep(self, duration):
        if self.interrupt:
            raise KeyboardInterrupt
        self.value += duration


def check_main(self, value):
    argv, graphs, expected_code, expected_fields, missing, interrupt = value
    clock = FakeClock(interrupt)
    index = 0

    def external(args):
        nonlocal index
        frame = graphs[min(max(index - 1, 0), len(graphs) - 1)]
        if args == ["pw-dump"]:
            raw = graphs[min(index, len(graphs) - 1)]
            index += 1
            return json.dumps(raw["graph"]) if isinstance(raw, dict) else raw
        if isinstance(frame, dict):
            if args[-1] == "GetModems":
                return f'a(oa{{sv}}) 1 "{GATEWAY}" 0'
            return external_responses(
                sink=frame.get("sink", "id 41,"),
                source=frame.get("source", "id 42,"),
                muted=frame.get("muted", "Volume: 0.5"),
                calls=frame.get("calls", "a(oa{sv}) 0"))(args)
        return external_responses()(args)

    output, errors = io.StringIO(), io.StringIO()
    with patch.object(sys, "argv", ["watch"] + argv), \
            patch.object(watch.shutil, "which", side_effect=lambda cmd: None if cmd == missing else "/fake/" + cmd), \
            patch.object(watch, "command", side_effect=external), \
            patch.object(watch.time, "monotonic", side_effect=clock.monotonic), \
            patch.object(watch.time, "sleep", side_effect=clock.sleep), \
            contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
        try:
            code = watch.main()
        except SystemExit as error:
            code = error.code
    self.assertEqual(code, expected_code, errors.getvalue())
    for field in expected_fields:
        self.assertIn(field + "\n", output.getvalue())
    self.assertNotIn(SECRET, output.getvalue() + errors.getvalue())


main_cases = []
for name, argv in [
        ("minimum_seconds", ["--seconds", "5"]),
        ("above_minimum_seconds", ["--seconds", "6"]),
        ("below_maximum_seconds", ["--seconds", "89"]),
        ("maximum_seconds", ["--seconds", "90"]),
        ("minimum_interval", ["--interval-ms", "250"]),
        ("above_minimum_interval", ["--interval-ms", "251"]),
        ("below_maximum_interval", ["--interval-ms", "1999"]),
        ("maximum_interval", ["--interval-ms", "2000"]),
        ("defaults", [])]:
    main_cases.append((name, (argv, ["[]"], 0, ["probe_complete=yes", "call_observed=no"], None, False)))
add_cases(WatcherContracts, "N2", "watch_runs_within_limits", main_cases, check_main)
add_cases(WatcherContracts, "N1", "watch_rejects_parameters", [
    ("invalid_" + str(i), (argv, ["[]"], 2, [], None, False))
    for i, argv in enumerate([
        ["--seconds", "4"], ["--seconds", "91"], ["--seconds", "0"],
        ["--seconds", "-1"], ["--seconds", "NaN"], ["--seconds", "Infinity"],
        ["--seconds", "5.5"], ["--seconds"], ["--interval-ms", "249"],
        ["--interval-ms", "2001"], ["--interval-ms", "0"],
        ["--interval-ms", "text"], ["--unknown"], ["extra"]])], check_main)
add_cases(WatcherContracts, "N7", "watch_tool_missing", [
    ("missing_" + cmd.replace("-", "_"), ([], ["[]"], 1,
       ["probe_error=read_only_tool_missing"], cmd, False))
    for cmd in ("pw-dump", "wpctl", "busctl")], check_main)
add_cases(WatcherContracts, "N9", "watch_interrupted", [
    ("keyboard_interrupt", ([], ["[]"], 130, ["probe_complete=interrupted"], None, True))], check_main)
add_cases(WatcherContracts, "N3", "watch_failed_samples", [
    ("all_failed_samples", (["--seconds", "5", "--interval-ms", "2000"], [None], 1,
      ["snapshots_succeeded=0", "snapshots_failed=3", "probe_complete=no"], None, False)),
    ("intermittent_samples", (["--seconds", "5", "--interval-ms", "2000"], [None, "[]"], 0,
      ["snapshots_succeeded=2", "snapshots_failed=1", "observed_state_versions=1"], None, False)),
], check_main)
add_cases(WatcherContracts, "N5", "watch_detects_state_changes", [
    ("stream_suspended", (["--seconds", "5", "--interval-ms", "2000"], [json.dumps([
        node(50, "Stream/Output/Audio", "suspended")])], 0,
        ["output_stream_disruption_observed=yes"], None, False)),
    ("stream_idle", (["--seconds", "5", "--interval-ms", "2000"], [json.dumps([
        node(50, "Stream/Output/Audio", "idle")])], 0,
        ["output_stream_disruption_observed=yes"], None, False)),
    ("hfp_node", (["--seconds", "5", "--interval-ms", "2000"], [json.dumps([
        node(50, **{"api.bluez5.profile": "headset-head-unit"})])], 0,
        ["hfp_nodes_observed=yes"], None, False)),
], check_main)

add_cases(WatcherContracts, "N5", "watch_tracks_routes_and_call", [
    ("route_and_call_transitions", (["--seconds", "5", "--interval-ms", "2000"], [
        {"graph": [node(41), node(42, "Audio/Source")]},
        {"graph": [node(43), node(44, "Audio/Source")], "sink": "id 43,",
         "source": "id 44,", "muted": "Volume: 0.5 [MUTED]",
         "calls": f'a(oa{{sv}}) 1 "{GATEWAY}/call0" 0'},
        {"graph": [node(41), node(42, "Audio/Source")]},
    ], 0, ["call_observed=yes", "sink_muted_at_any_time=yes",
           "default_sink_changed_at_any_time=yes", "default_source_changed=yes",
           "observed_state_versions=3"], None, False)),
], check_main)

def check_emit(self, value):
    first_sink, sink, first_source, source, sink_changed, source_changed = value
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        watch.emit(2, 0.9, empty_snapshot(), first_sink, sink, first_source, source)
    self.assertIn(f"default_sink_changed={sink_changed}\n", output.getvalue())
    self.assertIn(f"default_source_changed={source_changed}\n", output.getvalue())
    self.assertIn("sample=2\n", output.getvalue())
    self.assertIn("elapsed_seconds=0\n", output.getvalue())


add_cases(WatcherContracts, "Positive", "emit_routes", [
    ("same_routes", (1, 1, 2, 2, "no", "no")),
    ("changed_sink", (1, 3, 2, 2, "yes", "no")),
    ("changed_source", (1, 1, 2, 3, "no", "yes")),
    ("lost_routes", (1, None, 2, None, "yes", "yes")),
], check_emit)
