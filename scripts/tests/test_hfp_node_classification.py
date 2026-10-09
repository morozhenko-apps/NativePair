"""HFP profile/class contracts and anonymous end-of-wait observations."""
import json
from pathlib import Path
import sys
import unittest

from scenarios import add_cases
from probe_harness import DEVICE, assert_safe, commands, route, run_probe
from test_audio_diagnostics_contract import row, top
from test_hfp_contract_extended import graph

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import probe_audio_graph as audio
import probe_call_audio_watch as watch

HEAD = "headset-head-unit"
GATEWAY = "headset-audio-gateway"
EMPTY = 'a{oa{sv}} 0'
CALL_PATH = '/org/pipewire/Telephony/ag0/call0'


def call(state):
    return f'a{{oa{{sv}}}} 1 "{CALL_PATH}" 1 "State" s "{state}"'


class HfpNodeContracts(unittest.TestCase):
    pass


def classify(self, value):
    # Arrange
    profile, media, recognized, direction = value
    props = {"api.bluez5.profile": profile, "media.class": media,
             "node.name": "PRIVATE_CONTACT"}
    # Act / Assert
    self.assertIs(audio.is_hfp(props), recognized)
    self.assertEqual(audio.hfp_direction(props), direction)


profiles = [HEAD, GATEWAY, None, "", "a2dp-sink", "other", HEAD.upper(),
            GATEWAY + "-suffix", [], {}, 1]
classes = ["Audio/Source", "Audio/Sink", "Stream/Output/Audio", "Stream/Input/Audio",
           "Audio/Source/Internal", "Audio/Sink/Internal", "Other", None, "", [], {}, 1]
for recognized in (True, False):
    cases = []
    for p, profile in enumerate(profiles):
        for m, media in enumerate(classes):
            accepted = profile in (HEAD, GATEWAY)
            if accepted != recognized:
                continue
            direction = None
            if accepted and media == "Audio/Source":
                direction = "source"
            elif accepted and media == "Audio/Sink":
                direction = "sink"
            elif profile == GATEWAY and media == "Stream/Output/Audio":
                direction = "source"
            elif profile == GATEWAY and media == "Stream/Input/Audio":
                direction = "sink"
            cases.append((f"profile_{p}_class_{m}", (profile, media, accepted, direction)))
    add_cases(HfpNodeContracts, "Positive" if recognized else "N6",
              "hfp_direction_classified", cases, classify)


def endpoints(self, value):
    # Arrange
    script, nodes, count, source, sink, default_source, default_sink = value
    is_sco = script == "probe-hfp-sco.sh"
    fields = [f"hfp_node_count={count}",
              "hfp_source_node_present=" + ("yes" if source else "no"),
              "hfp_sink_node_present=" + ("yes" if sink else "no")]
    if is_sco:
        ready = source and sink and count >= 2
        fields += ["hfp_nodes_ready=" + ("yes" if ready else "no")]
        if not ready:
            fields += ["sco_error=hfp_nodes_not_ready"]
    else:
        ready = True
        fields += ["default_source_is_phone_hfp=" + ("yes" if default_source else "no"),
                   "default_sink_is_phone_hfp=" + ("yes" if default_sink else "no")]
    # Act
    routes = [route("pw-dump", stdout=graph(nodes))]
    if not is_sco:
        routes += [route("wpctl", "SINK", "id 42, type Node"),
                   route("wpctl", "SOURCE", "id 41, type Node")]
    result = run_probe(script, args=("--dial",) if is_sco else (), routes=routes)
    # Assert
    assert_safe(self, result, 0 if ready else 1, fields)
    for method in ("Dial", "HangupAll", "Activate"):
        self.assertEqual(len(commands(result, method)), int(is_sco))
    self.assertNotIn("Traceback", result.stderr)
    self.assertFalse(result.state["call_exists"])
    if not is_sco:
        self.assertFalse(any(c[0] == "wpctl" and c[1] != "inspect"
                             for c in result.state["commands"]))


families = [(HEAD, "Audio/Source", "Audio/Sink"),
            (GATEWAY, "Audio/Source", "Audio/Sink"),
            (GATEWAY, "Stream/Output/Audio", "Stream/Input/Audio")]
for f, (profile, source_role, sink_role) in enumerate(families):
    source = (41, DEVICE, profile, source_role)
    sink = (42, DEVICE, profile, sink_role)
    variants = [
        ("duplex", [source, sink], 2, True, True, "Positive"),
        ("source_only", [source], 1, True, False, "N2"),
        ("sink_only", [sink], 1, False, True, "N2"),
        ("repeated_source", [source, (42, DEVICE, profile, source_role)], 2, True, False, "N2"),
        ("repeated_sink", [(41, DEVICE, profile, sink_role), sink], 2, False, True, "N2"),
        ("duplicate_id", [source, (41, DEVICE, profile, sink_role)], 1, False, True, "N2"),
        ("foreign_target", [(i, "02:00:00:00:00:02", p, r) for i, _, p, r in [source, sink]],
         0, False, False, "N7"),
        ("unknown_roles", [(41, DEVICE, profile, "Other"), (42, DEVICE, profile, "Other")],
         2, False, False, "N6"),
    ]
    for name, nodes, count, has_source, has_sink, category in variants:
        # Explicit defaults point to the fixture's source 41 and sink 42.
        final = {n[0]: n for n in nodes if n[1] == DEVICE}
        default_source = 41 in final and final[41][3] == "Audio/Source"
        default_sink = 42 in final and final[42][3] == "Audio/Sink"
        for script in ("probe-hfp-sco.sh", "probe-audio-routing.sh"):
            add_cases(HfpNodeContracts, category, "endpoints_classified",
                      [(f"family_{f}_{name}_{script.replace('-', '_').replace('.', '_')}",
                        (script, nodes, count, has_source, has_sink, default_source, default_sink))], endpoints)


def consumers(self, value):
    # Arrange
    consumer, profile = value
    objects = json.loads(graph([(41, DEVICE, profile, "Stream/Output/Audio")]))
    expected = int(profile in (HEAD, GATEWAY))
    # Act / Assert
    if consumer == "watcher":
        snapshot = watch.graph_snapshot(objects, None, None, "unknown", "yes")
        self.assertEqual(snapshot["hfp_nodes"], expected)
        self.assertEqual(snapshot["bluetooth_nodes"], 1)
        self.assertEqual(snapshot["output_streams"], 1)
        self.assertNotIn(DEVICE, json.dumps(snapshot))
    else:
        result = run_probe("probe-audio-health.sh", routes=[
            route("pw-dump", stdout=json.dumps(objects)),
            route("pw-top", stdout=top([row(error="0"), row(error="1")]))])
        assert_safe(self, result, 0, [f"hfp_nodes_with_err_growth={expected}",
                                    "bluetooth_nodes_with_err_growth=1"])
        for method in ("Dial", "HangupAll", "Activate"):
            self.assertEqual(commands(result, method), [])


add_cases(HfpNodeContracts, "Positive", "consumer_profile_counted", [
    (consumer + "_" + str(p), (consumer, profile))
    for consumer in ("watcher", "health") for p, profile in enumerate((HEAD, GATEWAY, "a2dp-sink"))
], consumers)


def lifecycle(self, value):
    # Arrange: no call at guard, then observed and answered, then final snapshot.
    final_call, call_exit, expected_call, final_transport, transport_exit, expected_transport = value
    routes = [route("pw-dump", stdout="[]"), route("busctl", "GetCalls", replies=[
        {"stdout": EMPTY}, {"stdout": call("active")}, {"stdout": call("active")},
        {"stdout": final_call, "exit": call_exit}]),
        route("busctl", r"get-property.*/ag0 .* State$", replies=[
            {"stdout": 's "idle"'}, {"stdout": 's "active"'},
            {"stdout": final_transport, "exit": transport_exit}]),
        route("busctl", r"get-property.*/call0 .* State$", exit=1)]
    # Act
    result = run_probe("probe-hfp-sco.sh", args=("--dial",), routes=routes)
    # Assert
    assert_safe(self, result, 1, ["sco_error=hfp_nodes_not_ready",
        f"call_state_after_node_wait={expected_call}",
        f"transport_state_after_node_wait={expected_transport}",
        "cleanup_hangup_accepted=yes"])
    self.assertEqual(len(commands(result, "Dial")), 1)
    self.assertEqual(len(commands(result, "HangupAll")), 1)
    self.assertEqual(len(commands(result, "Activate")), 0)
    self.assertFalse(result.state["call_exists"])
    lines = result.stdout.splitlines()
    self.assertLess(lines.index(f"call_state_after_node_wait={expected_call}"),
                    lines.index("cleanup_hangup_attempted=yes"))
    self.assertNotIn("human_audio_check_required=yes", lines)


call_cases = [(call("active"), 0, "active"), (EMPTY, 0, "absent"),
              (call("disconnected"), 0, "disconnected"),
              (f'a{{oa{{sv}}}} 1 "{CALL_PATH}" 0', 0, "unknown")]
transport_cases = [(f's "{state}"', 0, state) for state in ("idle", "pending", "active", "error")]
transport_cases += [('s "PRIVATE_CONTACT"', 0, "unknown"), ("PRIVATE_CONTACT", 1, "unknown")]
add_cases(HfpNodeContracts, "N9", "node_wait_state_observed", [
    (f"call_{c}_transport_{t}", (*cv, *tv))
    for c, cv in enumerate(call_cases) for t, tv in enumerate(transport_cases)
], lifecycle)
add_cases(HfpNodeContracts, "N9", "node_wait_other_call_state_observed", [
    (state, (call(state), 0, state, 's "active"', 0, "active"))
    for state in ("dialing", "alerting", "incoming", "waiting", "held")
], lifecycle)
add_cases(HfpNodeContracts, "N6", "node_wait_unknown_reply_preserved", [
    ("malformed", ("PRIVATE_CONTACT", 0, "unknown", 's "idle"', 0, "idle"))
], lifecycle)
add_cases(HfpNodeContracts, "N3", "node_wait_failed_query_preserved", [
    ("query_failed", ("PRIVATE_CONTACT", 1, "unknown", 's "idle"', 0, "idle"))
], lifecycle)
add_cases(HfpNodeContracts, "Positive", "node_wait_legacy_empty_observed", [
    ("legacy_empty", ('a(oa{sv}) 0', 0, "absent", 's "idle"', 0, "idle"))
], lifecycle)
