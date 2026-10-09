"""Read-only audio routing and health classification with private fake graphs."""
import json
import unittest

from scenarios import add_cases
from probe_harness import run_probe, route, assert_safe, commands, DEVICE
from test_hfp_contract_extended import graph

ROUTING, HEALTH = "probe-audio-routing.sh", "probe-audio-health.sh"


class AudioDiagnosticsContracts(unittest.TestCase):
    pass


def check(self, value):
    script, routes, fields, expected, env = value
    result = run_probe(script, routes=routes, env=env)
    assert_safe(self, result, expected, fields)
    self.assertNotIn("Traceback", result.stderr)
    self.assertFalse(any(commands(result, method) for method in ("Dial", "HangupAll", "Activate", "PushMessage")))
    self.assertFalse(any(cmd[0] == "wpctl" and cmd[1] not in ("inspect", "get-volume")
                         for cmd in result.state["commands"]))


routing = [
    ("normal_hfp", (ROUTING, [], ["hfp_node_count=2", "default_sink_is_phone_hfp=yes", "default_source_is_phone_hfp=yes"], 0, {})),
    ("empty_graph", (ROUTING, [route("pw-dump", stdout="[]")], ["hfp_node_count=0", "orphan_hfp_nodes_present=no"], 0, {})),
    ("no_gateway", (ROUTING, [route("busctl", "GetModems", "a(oa{sv}) 0")], ["transport_state=unavailable"], 0, {})),
    ("failed_gateway", (ROUTING, [route("busctl", "GetModems", exit=1)], ["telephony_audio_gateway_present=no"], 0, {})),
    ("failed_state", (ROUTING, [route("busctl", "get-property", exit=1)], ["transport_state=unknown"], 0, {})),
    ("private_state", (ROUTING, [route("busctl", "get-property", 's "PRIVATE_CONTACT"')], ["transport_state=unknown"], 0, {})),
]
for target in ("SINK", "SOURCE"):
    for status in (0, 1):
        routing.append(("missing_" + target.lower() + str(status), (ROUTING,
            [route("wpctl", target, "PRIVATE_CONTACT", exit=status)],
            ["default_" + target.lower() + "_snapshot_available=no", "default_" + target.lower() + "_is_phone_hfp=no"], 0, {})))
for name, nodes, sources, sinks in [
    ("source_only", [(41, DEVICE, "headset-head-unit", "Audio/Source")], "yes", "no"),
    ("sink_only", [(41, DEVICE, "headset-head-unit", "Audio/Sink")], "no", "yes"),
    ("wrong_profile", [(41, DEVICE, "a2dp-sink", "Audio/Sink")], "no", "no"),
    ("wrong_device", [(41, "02:00:00:00:00:02", "headset-head-unit", "Audio/Sink")], "no", "no"),
    ("other_role", [(41, DEVICE, "headset-head-unit", "Other")], "no", "no"),
]:
    routing.append((name, (ROUTING, [route("pw-dump", stdout=graph(nodes))],
                          ["hfp_source_node_present=" + sources, "hfp_sink_node_present=" + sinks], 0, {})))
add_cases(AudioDiagnosticsContracts, "Positive", "routing_classified", routing, check)

add_cases(AudioDiagnosticsContracts, "N6", "audio_snapshot_rejected", [
    (script.replace("-", "_").replace(".", "_") + str(index), (script,
        [route("pw-dump", stdout=text)], ["pipewire_snapshot_valid=no"], 1, {}))
    for script in (ROUTING, HEALTH) for index, text in enumerate(("PRIVATE_CONTACT", "{}", "null", "3", '"PRIVATE_CONTACT"'))], check)
add_cases(AudioDiagnosticsContracts, "N6", "audio_entries_filtered", [
    (script.replace("-", "_").replace(".", "_") + str(index), (script,
        [route("pw-dump", stdout=json.dumps(entries))], ["probe_complete=yes"], 0, {}))
    for script in (ROUTING, HEALTH) for index, entries in enumerate((
        [None, 1, "PRIVATE_CONTACT"],
        [{"type": "PipeWire:Interface:Node", "id": 1, "info": "PRIVATE_CONTACT"}],
        [{"type": "PipeWire:Interface:Node", "id": 1, "info": {"props": "PRIVATE_CONTACT"}}],
        [{"type": "Other", "info": {}}],
        [{"type": "PipeWire:Interface:Node", "info": {}}],
    ))], check)
add_cases(AudioDiagnosticsContracts, "N3", "snapshot_tool_failed", [
    (script.replace("-", "_").replace(".", "_"), (script,
        [route("pw-dump", stderr="PRIVATE_CONTACT", exit=1)], ["pipewire_snapshot_available=no"], 1, {}))
    for script in (ROUTING, HEALTH)], check)


def top(rows):
    return "S   ID  QUANT RATE WAIT BUSY W/Q B/Q ERR FORMAT NAME\n" + "\n".join(rows) + "\n"


def row(state="R", identifier="41", quantum="256", rate="48000", error="0"):
    return f"{state} {identifier} {quantum} {rate} 0 0 0 0 {error} PRIVATE_CONTACT"


health = []
for state in ("E", "C", "S", "I", "R", "t", "T", "!"):
    health.append(("top_state_" + state.replace("!", "bang"), (HEALTH, [route("pw-top", stdout=top([row(state=state)]))],
        ["pw_top_rows_parsed=1", "running_rows_observed=" + str(int(state in ("R", "t", "T"))),
         "error_state_rows_observed=" + str(int(state == "E")), "nodes_with_err_growth=0", "nonzero_quantum_rate_pair_count=1"], 0, {})))
for name, rows, expected in [
    ("empty_top", [], 0), ("blank_rows", ["", "   "], 0),
    ("short_row", ["R 41 256"], 0), ("unknown_state", [row(state="X")], 0),
    ("nonnumeric_id", [row(identifier="x")], 0), ("negative_id", [row(identifier="-1")], 0),
    ("nonnumeric_err", [row(error="x")], 0), ("negative_err", [row(error="-1")], 0),
    ("zero_quantum", [row(quantum="0")], 1), ("zero_rate", [row(rate="0")], 1),
    ("text_quantum", [row(quantum="x")], 1), ("text_rate", [row(rate="x")], 1),
]:
    health.append((name, (HEALTH, [route("pw-top", stdout=top(rows))],
                         ["pw_top_rows_parsed=" + str(expected), "nonzero_quantum_rate_pair_count=0"], 0, {})))
for name, errors, delta, positive in [("stable_zero", [0, 0], 0, 0), ("stable_nonzero", [5, 5], 0, 1),
                                    ("single_growth", [0, 1], 1, 1), ("large_growth", [1, 100], 99, 1),
                                    ("counter_reset", [100, 0], 0, 0), ("peak_then_reset", [0, 3, 0], 3, 0)]:
    health.append((name, (HEALTH, [route("pw-top", stdout=top([row(error=str(e)) for e in errors]))],
        ["max_single_node_err_delta=" + str(delta), "nodes_with_nonzero_err_at_end=" + str(positive),
         "nodes_with_err_growth=" + str(int(delta > 0)), "default_sink_err_delta=" + str(delta)], 0, {})))
for name, props, expected in [
    ("bluetooth_address", {"api.bluez5.address": "PRIVATE_CONTACT"}, ["bluetooth_nodes_with_err_growth=1"]),
    ("bluetooth_api", {"device.api": "bluez5"}, ["bluetooth_nodes_with_err_growth=1"]),
    ("bluetooth_profile", {"api.bluez5.profile": "a2dp-sink"}, ["bluetooth_nodes_with_err_growth=1", "hfp_nodes_with_err_growth=0"]),
    ("hfp_profile", {"api.bluez5.profile": "headset-head-unit"}, ["bluetooth_nodes_with_err_growth=1", "hfp_nodes_with_err_growth=1"]),
    ("output_stream", {"media.class": "Stream/Output/Audio"}, ["output_stream_nodes_with_err_growth=1"]),
    ("audio_sink", {"media.class": "Audio/Sink"}, ["audio_sink_nodes_with_err_growth=1"]),
    ("audio_source", {"media.class": "Audio/Source"}, ["audio_source_nodes_with_err_growth=1", "default_source_err_delta=0"]),
    ("unclassified", {"media.class": "Other"}, ["unclassified_nodes_with_err_growth=1"]),
    ("missing_props", {}, ["unclassified_nodes_with_err_growth=1"]),
]:
    objects = [{"id": 41, "type": "PipeWire:Interface:Node", "info": {"props": props}}]
    health.append((name, (HEALTH, [route("pw-dump", stdout=json.dumps(objects))], expected, 0, {})))
for field in ("SINK", "SOURCE"):
    health.append(("missing_default_" + field.lower(), (HEALTH, [route("wpctl", field, exit=1)],
        ["default_" + field.lower() + "_snapshot_available=no", "default_" + field.lower() + "_is_bluetooth=unknown"], 0, {})))
for state in ("S", "I", "R", "t", "T"):
    health.append(("growth_while_" + state, (HEALTH, [route("pw-top", stdout=top([row(state=state, error="0"), row(state=state, error="1")]))],
        ["nodes_with_err_growth_while_running=" + str(int(state in ("R", "t", "T")))], 0, {})))
for iterations in ("2", "3", "59", "60", "08"):
    health.append(("iterations_" + iterations, (HEALTH, [], ["observation_iterations=" + str(int(iterations))], 0,
                                              {"NATIVEPAIR_AUDIO_HEALTH_ITERATIONS": iterations})))
add_cases(AudioDiagnosticsContracts, "N2", "health_counters_classified", health, check)

add_cases(AudioDiagnosticsContracts, "N3", "health_tool_failed", [
    ("pw_top_" + str(code), (HEALTH, [route("pw-top", exit=code)], ["pw_top_capture_succeeded=no", "pw_top_exit_status=" + str(code)], 1, {}))
    for code in (1, 124)], check)
add_cases(AudioDiagnosticsContracts, "N3", "health_services_failed", [
    ("service_" + service, (HEALTH, [route("systemctl", service, exit=1)], [field + "=no"], 0, {}))
    for service, field in (("pipewire.service", "pipewire_service_active"), ("wireplumber.service", "wireplumber_service_active"))], check)
add_cases(AudioDiagnosticsContracts, "N10", "private_journal_classified", [
    ("keyword_" + keyword, (HEALTH, [route("journalctl", stdout=keyword + " PRIVATE_CONTACT\n\nPRIVATE_CONTACT\n")],
        ["recent_pipewire_warning_lines=2", "recent_wireplumber_warning_lines=2", field + "=yes"], 0, {}))
    for keyword, field in [(word, "recent_audio_deadline_keywords") for word in ("xrun", "underrun", "overrun", "deadline", "missed")]
        + [(word, "recent_bluetooth_audio_warning_keywords") for word in ("bluez", "bluetooth", "sco", "hfp", "transport")]], check)
