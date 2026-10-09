"""HFP/SCO failure branches, policy, state races and owned-call teardown."""
import json
import unittest

from scenarios import add_cases, category
from probe_harness import run_probe, route, assert_safe, commands, DEVICE

HFP, AUDIO, CALL, SCO = ("probe-hfp.sh", "probe-hfp-audio.sh", "probe-hfp-call.sh", "probe-hfp-sco.sh")


class HfpContracts(unittest.TestCase):
    pass


def check(self, value):
    script, args, routes, config, fields, expected, dials, hangups, activates = value
    result = run_probe(script, args=args, routes=routes, config=config)
    assert_safe(self, result, expected, fields)
    self.assertNotIn("Traceback", result.stderr)
    self.assertEqual(len(commands(result, "Dial")), dials)
    self.assertEqual(len(commands(result, "HangupAll")), hangups)
    self.assertEqual(len(commands(result, "Activate")), activates)
    if hangups and "cleanup_hangup_accepted=no" not in result.stdout:
        self.assertFalse(result.state["call_exists"])


preflight = []
for script in (HFP, AUDIO, CALL, SCO):
    for name, routes, fields, expected in [
        ("normal", [], ["probe_complete=" + ("preflight" if script in (CALL, SCO) else "yes")], 0),
        ("hidden", [route("bluetoothctl", "info", "")], [], 1),
        ("unpaired", [route("bluetoothctl", "info", "Paired: no")], [], 1),
        ("no_hfp", [route("bluetoothctl", "info", "Paired: yes")], ["advertised_hfp_ag=no"], 1),
        ("connect_timeout", [route("timeout", "bluetoothctl connect", exit=124)], [], 0 if script == HFP else 1),
        ("already_connected", [route("bluetoothctl", "connect", "already connected", exit=1)], [], 0),
        ("unconfirmed_connect", [route("bluetoothctl", "connect", "PRIVATE_CONTACT", exit=1)], [], 0),
        ("manager_error", [route("busctl", "GetModems", exit=1)], ["hfp_session_established=no"], 0 if script == HFP else 1),
        ("no_gateway", [route("busctl", "GetModems", "a(oa{sv}) 0")], ["hfp_session_established=no"], 0 if script == HFP else 1),
        ("ambiguous_gateway", [route("busctl", "GetModems", 'a(oa{sv}) 2 "/org/pipewire/Telephony/ag0" 0 "/org/pipewire/Telephony/ag1" 0')],
         ["hfp_session_established=no"], 0 if script == HFP else 1),
    ]:
        preflight.append((script.replace("-", "_").replace(".", "_") + "_" + name,
                          (script, (), routes, {}, fields, expected, 0, 0, 0)))
add_cases(HfpContracts, "N3", "hfp_preflight_evaluated", preflight, check)

add_cases(HfpContracts, "N6", "call_state_guard_checked", [
    (script.replace("-", "_").replace(".", "_") + "_" + name,
     (script, ("--dial",), [route("busctl", "GetCalls", text, exit=code)], {}, fields, 1, 0, 0, 0))
    for script in (CALL, SCO) for name, text, code, fields in [
        ("query_failed", "PRIVATE_CONTACT", 1, ["call_state_query_succeeded=no"]),
        ("empty_reply", "", 0, ["call_state_query_succeeded=no"]),
        ("malformed_reply", "PRIVATE_CONTACT", 0, ["call_state_query_succeeded=no"]),
        ("count_without_object", "a(oa{sv}) 1", 0, ["call_state_query_succeeded=no"]),
        ("existing_call", 'a(oa{sv}) 1 "/org/pipewire/Telephony/ag0/call0" 0', 0, ["preexisting_call_present=yes"]),
    ]], check)

add_cases(HfpContracts, "N7", "call_cleanup_owned", [
    (script.replace("-", "_").replace(".", "_") + "_" + name,
     (script, ("--dial",), routes, {}, fields, expected, dials, hangups, 0))
    for script in (CALL, SCO) for name, routes, fields, expected, dials, hangups in [
        ("ambiguous_dial", [route("busctl", "Dial s", "PRIVATE_CONTACT", exit=1)],
         ["cleanup_hangup_attempted=yes", "cleanup_hangup_accepted=yes"], 1, 1, 1),
        ("dial_terminated", [route("busctl", "Dial s", signal_parent="SIGTERM")],
         ["cleanup_hangup_attempted=yes", "cleanup_hangup_accepted=yes"], 143, 1, 1),
        ("pre_dial_terminated", [route("busctl", "GetCalls", "a(oa{sv}) 0", signal_parent="SIGTERM")],
         [], 143, 0, 0),
    ]], check)

add_cases(HfpContracts, "N3", "call_observation_and_hangup", [
    ("no_call_after_dial", (CALL, ("--dial",), [route("busctl", "GetCalls", "a(oa{sv}) 0")], {},
                            ["call_object_observed=no", "probe_complete=inconclusive"], 0, 1, 1, 0)),
    ("hangup_failed_twice", (CALL, ("--dial",), [route("busctl", "HangupAll", exit=1)], {},
                             ["call_error=hangup_failed", "cleanup_hangup_accepted=no"], 1, 1, 2, 0)),
    ("hangup_retry_cleanup", (CALL, ("--dial",), [route("busctl", "HangupAll", replies=[{"exit": 1}, {"delegate": True}])], {},
                             ["call_error=hangup_failed", "cleanup_hangup_accepted=yes"], 1, 1, 2, 0)),
], check)

audio_cases = []
for prop, field in [("State", "transport_state_readable"), ("Codec", "transport_codec_readable"), ("RejectSCO", "reject_sco_readable")]:
    audio_cases.append(("failed_" + prop, (AUDIO, (), [route("busctl", "get-property.*" + prop, exit=1)], {}, [field + "=no"], 1, 0, 0, 0)))
for codec, expected in [("0", "unknown"), ("1", "cvsd"), ("2", "msbc"), ("3", "lc3_swb"), ("255", "unknown"), ("256", "unknown"), ("x", "unknown")]:
    audio_cases.append(("codec_" + codec, (AUDIO, (), [route("busctl", "Codec", "y " + codec)], {}, ["transport_codec=" + expected], 0, 0, 0, 0)))
for state in ("idle", "pending", "active", "error", "PRIVATE_CONTACT", ""):
    audio_cases.append(("state_" + (state or "empty"), (AUDIO, (), [route("busctl", "get-property.*State", 's "' + state + '"')], {},
                       ["transport_state=" + (state if state in ("idle", "pending", "active", "error") else "unknown")], 0, 0, 0, 0)))
for value, expected in [("true", "yes"), ("false", "no"), ("PRIVATE_CONTACT", "unknown")]:
    audio_cases.append(("reject_" + value, (AUDIO, (), [route("busctl", "RejectSCO", "b " + value)], {}, ["reject_sco=" + expected], 0, 0, 0, 0)))
add_cases(HfpContracts, "N6", "audio_properties_classified", audio_cases, check)

add_cases(HfpContracts, "N7", "sco_policy_checked", [
    (name, (SCO, ("--dial",), [route("busctl", match, text, exit=code)], {}, fields, 1, 0, 0, 0))
    for name, match, text, code, fields in [
        ("reject_enabled", "RejectSCO", "b true", 0, ["probe_complete=blocked"]),
        ("reject_corrupt", "RejectSCO", "PRIVATE_CONTACT", 0, ["reject_sco=unknown"]),
        ("reject_unavailable", "RejectSCO", "", 1, ["reject_sco_readable=no"]),
        ("no_transport_interface", "introspect", "org.pipewire.Telephony.AudioGateway1 Dial", 0, ["transport_interface_available=no"]),
        ("no_activate", "introspect", "org.pipewire.Telephony.AudioGatewayTransport1", 0, ["transport_activate_api_available=no"]),
    ]], check)

add_cases(HfpContracts, "N9", "sco_call_not_active", [
    ("call_" + state, (SCO, ("--dial",), [], {"active_calls": 'a(oa{sv}) 1 "/org/pipewire/Telephony/ag0/call0" 1 "State" s "' + state + '"'},
                         ["sco_error=call_not_active"], 1, 1, 1, 0))
    for state in ("dialing", "alerting", "incoming", "waiting", "held", "disconnected")], check)

add_cases(HfpContracts, "N6", "sco_call_fallback", [
    ("fallback_" + str(index), (SCO, ("--dial",), routes, {"active_calls": 'a(oa{sv}) 1 "/org/pipewire/Telephony/ag0/call1" 0'},
                               ["call_active_observed=" + active], expected, 1, 1, activates))
    for index, routes, active, expected, activates in [
        (0, [], "yes", 0, 1),
        (1, [route("busctl", "get-property.*org.pipewire.Telephony.Call1", exit=1)], "yes", 0, 1),
        (2, [route("busctl", "get-property.*/call1.*State", exit=1)], "no", 1, 0),
        (3, [route("busctl", "get-property.*/call1.*State", 's "PRIVATE_CONTACT"')], "no", 1, 0),
    ]], check)

add_cases(HfpContracts, "N3", "sco_call_object_lost", [
    ("no_object", (SCO, ("--dial",), [route("busctl", "GetCalls", "a(oa{sv}) 0")], {},
                   ["sco_error=no_call_object"], 1, 1, 1, 0)),
    ("query_lost", (SCO, ("--dial",), [route("busctl", "GetCalls", replies=[{"stdout": "a(oa{sv}) 0"}, {"exit": 1}])], {},
                    ["sco_error=no_call_object"], 1, 1, 1, 0)),
], check)

transport_cases = []
for name, sequence, fields, expected, activates in [
    ("pending_active", ["idle", "pending", "active"], ["transport_activation_path=pending_wait"], 0, 0),
    ("pending_idle", ["idle", "pending", "idle"], ["sco_error=transport_not_active"], 1, 0),
    ("pending_error", ["idle", "pending", "error"], ["sco_error=transport_not_active"], 1, 0),
    ("pending_timeout", ["idle", "pending"], ["sco_error=transport_not_active"], 1, 0),
    ("unknown_state", ["idle", "PRIVATE_CONTACT"], ["transport_state_before_activate=unknown", "sco_error=transport_not_active"], 1, 0),
    ("error_state", ["idle", "error"], ["sco_error=transport_not_active"], 1, 0),
    ("accepted_pending_timeout", ["idle", "idle", "pending"], ["sco_error=transport_not_active"], 1, 1),
    ("accepted_error", ["idle", "idle", "error"], ["sco_error=transport_not_active"], 1, 1),
]:
    transport_cases.append((name, (SCO, ("--dial",), [route("busctl", "get-property.*/ag0 .*State", replies=[{"stdout": 's "' + state + '"'} for state in sequence])], {},
                            fields, expected, 1, 1, activates)))
add_cases(HfpContracts, "N5", "sco_transport_transition", transport_cases, check)

errors = ["org.pipewire.Telephony.Error." + name for name in ("InvalidState", "InvalidFormat", "NotSupported", "InProgress", "Failed", "CME")]
errors += ["org.freedesktop.DBus.Error." + name for name in ("InvalidArgs", "Failed", "NoReply", "Timeout", "AccessDenied", "ServiceUnknown")]
errors += ["timed out", "timeout", "invalid state", "already active", "PRIVATE_CONTACT"]
add_cases(HfpContracts, "N3", "activate_error_allowlisted", [
    ("error_" + str(index), (SCO, ("--dial",), [route("busctl", " Activate$", text, exit=1)], {},
                            ["activate_error_class=" + (text if text.startswith("org.") else "timeout" if text in ("timed out", "timeout") else "invalid_state" if text in ("invalid state", "already active") else "unknown"),
                             "cleanup_hangup_accepted=yes"], 1, 1, 1, 1))
    for index, text in enumerate(errors)], check)


def graph(nodes):
    return json.dumps([{"id": identifier, "type": "PipeWire:Interface:Node", "info": {"props": {
        "api.bluez5.address": device, "api.bluez5.profile": profile, "media.class": role}}}
        for identifier, device, profile, role in nodes])


add_cases(HfpContracts, "N6", "sco_endpoints_required", [
    ("nodes_" + str(index), (SCO, ("--dial",), [route("pw-dump", stdout=text)], {},
                            ["sco_error=hfp_nodes_not_ready"], 1, 1, 1, 1))
    for index, text in enumerate([
        "[]", "PRIVATE_CONTACT", "{}", '[null,1,"PRIVATE_CONTACT"]',
        graph([(41, DEVICE, "headset-head-unit", "Audio/Source")]),
        graph([(41, DEVICE, "headset-head-unit", "Audio/Sink")]),
        graph([(41, "02:00:00:00:00:02", "headset-head-unit", "Audio/Source"), (42, "02:00:00:00:00:02", "headset-head-unit", "Audio/Sink")]),
        graph([(41, DEVICE, "a2dp-sink", "Audio/Source"), (42, DEVICE, "a2dp-sink", "Audio/Sink")]),
        graph([(41, DEVICE, "headset-head-unit", "Other"), (42, DEVICE, "headset-head-unit", "Other")]),
        graph([(41, DEVICE, "headset-head-unit", "Audio/Source"), (42, DEVICE, "headset-head-unit", "Audio/Source")]),
        graph([(41, DEVICE, "headset-head-unit", "Audio/Source"), (41, DEVICE, "headset-head-unit", "Audio/Sink")]),
    ])], check)
add_cases(HfpContracts, "N3", "sco_endpoint_and_hangup_failure", [
    ("dump_failed", (SCO, ("--dial",), [route("pw-dump", exit=1)], {}, ["sco_error=hfp_nodes_not_ready"], 1, 1, 1, 1)),
    ("hangup_failed", (SCO, ("--dial",), [route("busctl", "HangupAll", exit=1)], {}, ["sco_error=hangup_failed", "cleanup_hangup_accepted=no"], 1, 1, 2, 1)),
], check)
