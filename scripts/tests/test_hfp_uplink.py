"""Exhaustive direct-uplink contracts with synthetic graphs and read adapters."""

import contextlib
import io
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from scenarios import add_cases

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import probe_hfp_uplink as uplink

TARGET = "AA:BB:CC:DD:EE:FF"
FOREIGN = "02:00:00:00:00:01"
PRIVATE = "PRIVATE_CONTACT_+15551234567"
READS = [["pw-dump"], ["wpctl", "inspect", "@DEFAULT_AUDIO_SOURCE@"],
         ["wpctl", "get-volume", "@DEFAULT_AUDIO_SOURCE@"]]


def node(nid, role="Audio/Source", api="alsa", state="running", **props):
    return {"id": nid, "type": "PipeWire:Interface:Node", "info": {
        "state": state, "props": {"media.class": role, "device.api": api, **props}}}


def endpoint(nid=60, profile="headset-audio-gateway", role="Stream/Input/Audio", address=TARGET):
    return node(nid, role, "bluez5", **{
        "api.bluez5.profile": profile, "api.bluez5.address": address})


def link(origin=42, destination=60, state="active"):
    return {"type": "PipeWire:Interface:Link", "info": {
        "output-node-id": origin, "input-node-id": destination, "state": state}}


def expected(**changes):
    result = {"target_uplink_endpoints": 0, "active_direct_sources": 0,
              "active_direct_alsa_sources": 0, "default_source_present": "yes",
              "default_source_is_alsa": "yes", "default_source_state": "running",
              "default_source_directly_linked": "no"}
    result.update(changes)
    return result


def missing_default(**changes):
    return expected(default_source_present="no", default_source_is_alsa="unknown",
                    default_source_state="unknown", default_source_directly_linked="unknown",
                    **changes)


CONNECTED = expected(target_uplink_endpoints=1, active_direct_sources=1,
                     active_direct_alsa_sources=1, default_source_directly_linked="yes")


class UplinkContracts(unittest.TestCase):
    pass


def check_target(self, value):
    # Arrange
    target, accepted = value
    # Act
    actual = uplink._valid_target(target)
    snapshot = uplink.snapshot([], None, target)
    if not accepted:
        with patch.object(uplink, "command") as external:
            self.assertIsNone(uplink.sample(target))
        external.assert_not_called()
    # Assert
    self.assertIs(actual, accepted)
    self.assertEqual(snapshot, missing_default() if accepted else None)


add_cases(UplinkContracts, "Positive", "target_validated", [
    ("uppercase", (TARGET, True)), ("lowercase", (TARGET.lower(), True)),
    ("mixedcase", ("aA:Bb:cC:Dd:eE:Ff", True)), ("zero", ("00:00:00:00:00:00", True)),
], check_target)
add_cases(UplinkContracts, "N1", "target_rejected", [
    ("invalid_target_" + str(i), (target, False)) for i, target in enumerate([
        None, 1, True, [], {}, "", "AA", TARGET[:-1], TARGET + "F", TARGET + "\n",
        " " + TARGET, TARGET + " ", TARGET.replace(":", "-"),
        TARGET.replace("A", "G"), TARGET.replace("A", "Ａ"), PRIVATE,
        "00:11:22:33:44", "00:11:22:33:44:55:66"])
], check_target)


def check_graph(self, value):
    # Arrange
    graph, default, result = value
    # Act
    actual = uplink.snapshot(graph, default, TARGET)
    # Assert
    self.assertEqual(actual, result)
    self.assertNotIn(PRIVATE, str(actual))
    self.assertNotIn(TARGET, str(actual))


profiles = ("headset-head-unit", "headset-audio-gateway")
roles = ("Audio/Source", "Audio/Sink", "Stream/Output/Audio", "Stream/Input/Audio",
         "Audio/Filter", None, PRIVATE)
for foreign in (False, True):
    cases = []
    for pindex, profile in enumerate(profiles):
        for rindex, role in enumerate(roles):
            accepted = not foreign and (role == "Audio/Sink" or (
                profile == "headset-audio-gateway" and role == "Stream/Input/Audio"))
            cases.append((f"profile_{pindex}_role_{rindex}_foreign_{foreign}", (
                [node(42), endpoint(profile=profile, role=role,
                                    address=FOREIGN if foreign else TARGET.lower()), link()], 42,
                CONNECTED if accepted else expected())))
    add_cases(UplinkContracts, "N7" if foreign else "Positive", "direction_and_target_checked",
              cases, check_graph)

add_cases(UplinkContracts, "N6", "unknown_endpoints_ignored", [
    ("profile_" + str(i), ([node(42), endpoint(profile=profile), link()], 42, expected()))
    for i, profile in enumerate([None, [], {}, 1, True, "a2dp-sink", PRIVATE])
] + [
    ("address_" + str(i), ([node(42), endpoint(address=address), link()], 42, expected()))
    for i, address in enumerate([None, [], {}, 1, True, "", TARGET + " ", PRIVATE])
], check_graph)

add_cases(UplinkContracts, "N6", "invalid_roots_rejected", [
    ("root_" + str(i), (root, None, None))
    for i, root in enumerate([None, {}, "", PRIVATE, 1, True])
], check_graph)

add_cases(UplinkContracts, "N6", "invalid_nodes_and_links_ignored", [
    ("corrupt_" + str(i), ([node(42), endpoint(), obj], 42,
                           expected(target_uplink_endpoints=1)))
    for i, obj in enumerate([
        None, 1, [], PRIVATE, {}, {"type": "Other", "info": link()["info"]},
        {"type": "PipeWire:Interface:Link"},
        *({"type": "PipeWire:Interface:Link", "info": info}
          for info in [None, 0, False, [], PRIVATE, {}]),
        node(True), node(-1), node(4294967296),
        {"id": 70, "type": "PipeWire:Interface:Node", "info": []},
        {"id": 70, "type": "PipeWire:Interface:Node", "info": {"props": []}},
    ])
], check_graph)

add_cases(UplinkContracts, "N6", "inactive_links_ignored", [
    ("state_" + str(i), ([node(42), endpoint(), link(state=state)], 42,
                        CONNECTED if state == "active" else expected(target_uplink_endpoints=1)))
    for i, state in enumerate(["active", "paused", "init", "error", "unlinked", None,
                              "ACTIVE", PRIVATE, [], True])
], check_graph)

invalid_ids = [None, True, False, -1, 4294967296, 42.0, "42", [], {}, PRIVATE]
add_cases(UplinkContracts, "N6", "invalid_link_ids_ignored", [
    (f"endpoint_{side}_id_{i}", (
        [node(42), endpoint(), link(origin=value if side == 0 else 42,
                                    destination=value if side == 1 else 60)], 42,
        expected(target_uplink_endpoints=1)))
    for side in (0, 1) for i, value in enumerate(invalid_ids)
], check_graph)

add_cases(UplinkContracts, "N2", "uint32_link_boundaries", [
    (f"side_{side}_boundary_{value}", (
        [node(value if side == 0 else 42), endpoint(nid=value if side == 1 else 60),
         link(origin=value if side == 0 else 42, destination=value if side == 1 else 60)],
        value if side == 0 else 42, CONNECTED))
    for side in (0, 1) for value in (0, 1, 4294967294, 4294967295)
], check_graph)

add_cases(UplinkContracts, "N5", "stale_or_invalid_defaults", [
    ("default_" + str(i), ([node(42), endpoint(), link()], default,
                           missing_default(target_uplink_endpoints=1, active_direct_sources=1,
                                           active_direct_alsa_sources=1)))
    for i, default in enumerate([None, 999, True, False, [], {}, "42", 42.0, -1, 4294967296])
], check_graph)

add_cases(UplinkContracts, "N6", "default_states_allowlisted", [
    ("source_state_" + str(i), ([node(42, state=state), endpoint(), link()], 42,
         {**CONNECTED, "default_source_state": state if state in (
             "running", "idle", "suspended", "error") else "unknown"}))
    for i, state in enumerate(["running", "idle", "suspended", "error", None, PRIVATE, [], 1])
], check_graph)

add_cases(UplinkContracts, "Positive", "default_and_source_api_checked", [
    (f"api_{index}_origin_{origin}", (
        [node(42, api=api), node(43, api=api), endpoint(), link(origin=origin)], 42,
        expected(target_uplink_endpoints=1, active_direct_sources=1,
                 active_direct_alsa_sources=int(api == "alsa"),
                 default_source_is_alsa="yes" if api == "alsa" else "no",
                 default_source_directly_linked="yes" if origin == 42 else "no")))
    for index, api in enumerate(["alsa", "bluez5", "filter", None, PRIVATE]) for origin in (42, 43)
], check_graph)

add_cases(UplinkContracts, "N4", "distinct_origins_counted", [
    ("duplicate_channels", ([node(42), endpoint(), link(), link()], 42, CONNECTED)),
    ("duplicate_nodes", ([node(42), node(42), endpoint(), endpoint(), link()], 42, CONNECTED)),
    ("duplicate_id_last_wins", ([node(42), endpoint(), endpoint(address=FOREIGN), link()],
                               42, expected())),
    ("two_endpoints_one_source", ([node(42), endpoint(), endpoint(nid=61), link(), link(destination=61)],
                                  42, {**CONNECTED, "target_uplink_endpoints": 2})),
    ("two_sources", ([node(42), node(43), endpoint(), link(), link(origin=43)], 42,
                     {**CONNECTED, "active_direct_sources": 2, "active_direct_alsa_sources": 2})),
], check_graph)

add_cases(UplinkContracts, "N7", "unrelated_links_do_not_prove_uplink", [
    ("reversed", ([node(42), endpoint(), link(origin=60, destination=42)], 42,
                  expected(target_uplink_endpoints=1))),
    ("dangling_origin", ([node(42), endpoint(), link(origin=999)], 42,
                         expected(target_uplink_endpoints=1))),
    ("dangling_destination", ([node(42), endpoint(), link(destination=999)], 42,
                              expected(target_uplink_endpoints=1))),
    ("self_link", ([node(42), endpoint(), link(origin=60)], 42,
                   expected(target_uplink_endpoints=1))),
    ("wrong_default_class", ([node(42, "Audio/Sink"), endpoint(), link()], 42,
                             missing_default(target_uplink_endpoints=1))),
    ("filter_path_unproven", ([node(42), node(50, "Audio/Filter"), endpoint(),
                              link(destination=50), link(origin=50)], 42,
                             expected(target_uplink_endpoints=1))),
    ("bool_alias_origin", ([node(1), endpoint(), link(origin=True)], 1,
                           expected(target_uplink_endpoints=1))),
    ("bool_alias_destination", ([node(42), endpoint(nid=1), link(destination=True)], 42,
                                expected(target_uplink_endpoints=1))),
    ("bool_alias_default", ([node(1), endpoint(), link(origin=1)], True,
                            missing_default(target_uplink_endpoints=1, active_direct_sources=1,
                                            active_direct_alsa_sources=1))),
], check_graph)

add_cases(UplinkContracts, "N10", "private_fields_never_emitted", [
    ("private_graph_properties", ([node(42, **{"node.name": PRIVATE, "node.description": PRIVATE}),
                                  endpoint(), link(), node(70, state=PRIVATE)], 42, CONNECTED)),
], check_graph)


def adapter(raw, source, mute, calls, interrupt=False):
    def read(args):
        calls.append(args)
        if interrupt:
            raise KeyboardInterrupt
        return {tuple(READS[0]): raw, tuple(READS[1]): source, tuple(READS[2]): mute}[tuple(args)]
    return read


def check_sample(self, value):
    # Arrange
    raw, source, mute, result, expected_reads = value
    calls = []
    # Act
    with patch.object(uplink, "command", side_effect=adapter(raw, source, mute, calls)):
        actual = uplink.sample(TARGET)
    # Assert
    self.assertEqual(actual, result)
    self.assertEqual(calls, READS[:expected_reads])
    self.assertNotIn(PRIVATE, str(actual))


add_cases(UplinkContracts, "N6", "dump_failures_are_unknown", [
    ("dump_" + str(i), (raw, "id 42,", "Volume: 0.5", None,
                        1 if raw is None or raw.startswith("{") and raw != "{}" else 2))
    for i, raw in enumerate([None, "{" + PRIVATE, "{}", "null", "5", json.dumps(PRIVATE)])
], check_sample)
add_cases(UplinkContracts, "N3", "default_read_failure_is_unknown", [
    ("source_read_" + str(i), (json.dumps([node(42), endpoint(), link()]), source, None,
                              {**missing_default(target_uplink_endpoints=1, active_direct_sources=1,
                                                 active_direct_alsa_sources=1),
                               "default_source_muted": "unknown"}, 3))
    for i, source in enumerate([None, "", PRIVATE, "id 999,", "id 4294967296,"])
], check_sample)
add_cases(UplinkContracts, "Positive", "sample_preserves_classification", [
    ("source_mute_" + str(i), (json.dumps([node(42), endpoint(), link()]), "id 42,", mute,
                              {**CONNECTED, "default_source_muted": state}, 3))
    for i, (mute, state) in enumerate([
        ("Volume: 0.5", "no"), ("Volume: 0.5 [MUTED]", "yes"),
        (None, "unknown"), (PRIVATE, "unknown")])
], check_sample)
add_cases(UplinkContracts, "N6", "empty_or_corrupt_entries_are_unknown_defaults", [
    ("empty_graph", ("[]", "id 42,", "Volume: 0.5",
                     {**missing_default(), "default_source_muted": "no"}, 3)),
    ("corrupt_entries", ('[null,3,"private"]', "id 42,", "Volume: 0.5",
                         {**missing_default(), "default_source_muted": "no"}, 3)),
], check_sample)


def check_main(self, value):
    # Arrange
    args, target, missing, raw, interrupt, code, fields = value
    calls, output, errors = [], io.StringIO(), io.StringIO()
    # Act
    with patch.object(sys, "argv", ["uplink", *args]), \
            patch.dict(uplink.os.environ, {} if target is None else {"NATIVEPAIR_DEVICE": target}, clear=True), \
            patch.object(uplink.shutil, "which", side_effect=lambda tool: None if tool == missing else "/fake"), \
            patch.object(uplink, "command", side_effect=adapter(raw, "id 42,", "Volume: 0.5", calls, interrupt)), \
            contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
        actual = uplink.main()
    # Assert
    self.assertEqual(actual, code)
    self.assertEqual(errors.getvalue(), "")
    for field in fields:
        self.assertIn(field, output.getvalue().splitlines())
    for secret in (PRIVATE, TARGET, FOREIGN):
        self.assertNotIn(secret, output.getvalue())
    if code == 2 or missing is not None or args:
        self.assertEqual(calls, [])
    else:
        self.assertEqual(calls, READS[:1] if interrupt or raw is None else READS)


add_cases(UplinkContracts, "Positive", "cli_success_or_help", [
    ("success", ([], TARGET, None, json.dumps([node(42), endpoint(), link()]), False, 0,
                 ["probe_complete=yes", "default_source_directly_linked=yes", "call_performed=no",
                  "audio_configuration_changed=no", "active_direct_alsa_sources=1"])),
    ("idle", ([], TARGET, None, json.dumps([node(42)]), False, 0,
              ["probe_complete=yes", "target_uplink_endpoints=0", "default_source_directly_linked=no"])),
    ("help", (["--help"], None, None, None, False, 0, [])),
    ("short_help", (["-h"], None, None, None, False, 0, [])),
], check_main)
add_cases(UplinkContracts, "N1", "cli_rejects_arguments_privately", [
    ("argument_" + str(i), (args, TARGET, None, None, False, 2,
                            ["probe_error=arguments_not_supported"]))
    for i, args in enumerate([[PRIVATE], ["--unknown", PRIVATE], ["--help", PRIVATE], [""]])
], check_main)
add_cases(UplinkContracts, "N7", "cli_requires_target_and_tools", [
    ("target_" + str(i), ([], target, None, None, False, 2,
                          ["probe_error=invalid_or_missing_target"]))
    for i, target in enumerate([None, "", PRIVATE, TARGET + "\n"])
] + [
    ("tool_" + tool, ([], TARGET, tool, None, False, 1, ["probe_error=read_only_tool_missing"]))
    for tool in ("pw-dump", "wpctl")
], check_main)
add_cases(UplinkContracts, "N3", "cli_read_failure_fails", [
    ("failed_dump", ([], TARGET, None, None, False, 1,
                     ["probe_error=graph_snapshot_unavailable", "probe_complete=no"]))
], check_main)
add_cases(UplinkContracts, "N9", "cli_interrupt_does_not_retry", [
    ("interrupted_read", ([], TARGET, None, None, True, 130, ["probe_complete=interrupted"]))
], check_main)
