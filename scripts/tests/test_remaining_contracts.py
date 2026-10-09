"""Additional independent branch/interaction rows identified during coverage audit."""
import json
import unittest

from scenarios import add_cases, category
from probe_harness import run_probe, route, assert_safe, commands, DEVICE


class RemainingProbeContracts(unittest.TestCase):
    pass


def check(self, value):
    script, args, env, routes, config, missing, fields, code = value
    result = run_probe(script, args=args, env=env, routes=routes, config=config, missing=missing)
    assert_safe(self, result, code, fields)


cases = []
for script, variables in (
    ("probe-obex-session.sh", ["NATIVEPAIR_OBEX_TIMEOUT"]),
    ("probe-obex-read.sh", ["NATIVEPAIR_OBEX_TIMEOUT"]),
    ("probe-map-send.sh", ["NATIVEPAIR_OBEX_TIMEOUT", "NATIVEPAIR_SEND_TIMEOUT"]),
    ("probe-map-events.sh", ["NATIVEPAIR_OBEX_TIMEOUT", "NATIVEPAIR_EVENT_TIMEOUT"]),
    ("probe-hfp.sh", ["NATIVEPAIR_HFP_CONNECT_TIMEOUT"]),
    ("probe-hfp-audio.sh", ["NATIVEPAIR_HFP_CONNECT_TIMEOUT"]),
    ("probe-hfp-call.sh", ["NATIVEPAIR_CALL_OBSERVE_SECONDS"]),
    ("probe-hfp-sco.sh", ["NATIVEPAIR_HFP_CONNECT_TIMEOUT", "NATIVEPAIR_SCO_STATE_TIMEOUT", "NATIVEPAIR_CALL_ACTIVE_TIMEOUT", "NATIVEPAIR_SCO_HUMAN_WINDOW"]),
):
    for variable in variables:
        for boundary in ("922337203685477579", "922337203685477580"):
            args = ("--target", "map") if "obex-" in script else ()
            # Stop after validation via a deliberately missing dependency;
            # a huge accepted limit is never allowed into a polling loop.
            cases.append((script.replace("-", "_").replace(".", "_") + variable + boundary,
                (script, args, {variable: boundary}, [], {}, ("busctl",), [], 1)))
add_cases(RemainingProbeContracts, "N2", "timer_capacity_boundary_accepted", cases, check)

add_cases(RemainingProbeContracts, "Positive", "device_argument_overrides_environment", [
    ("bluetooth_override", ("probe-bluetooth.sh", ("--device", DEVICE), {"NATIVEPAIR_DEVICE": "bad"}, [], {}, (), ["device_visible=yes"], 0)),
    ("bluetooth_host_after_device", ("probe-bluetooth.sh", ("--device", DEVICE, "--host-only"), {}, [], {}, (), ["probe_scope=host"], 0)),
    ("bluetooth_device_after_host", ("probe-bluetooth.sh", ("--host-only", "--device", DEVICE), {}, [], {}, (), ["probe_scope=host+device"], 0)),
    ("session_override", ("probe-obex-session.sh", ("--device", DEVICE, "--target", "map"), {"NATIVEPAIR_DEVICE": "bad"}, [], {}, (), ["session_established=yes"], 0)),
    ("read_override", ("probe-obex-read.sh", ("--device", DEVICE, "--target", "map"), {"NATIVEPAIR_DEVICE": "bad"}, [], {}, (), ["read_probe_complete=yes"], 0)),
], check)

add_cases(RemainingProbeContracts, "N6", "hfp_interfaces_absent", [
    ("interface_" + str(index), (script, (), {}, routes, {}, (), fields, code))
    for index, (script, routes, fields, code) in enumerate([
        ("probe-hfp.sh", [route("busctl", "introspect", exit=1)], ["telephony_service_available=no", "telephony_manager_api_available=no", "call_control_api_available=no"], 0),
        ("probe-hfp.sh", [route("busctl", "introspect", "org.other")], ["telephony_manager_api_available=no", "call_control_api_available=no", "call_state_api_available=no"], 0),
        ("probe-hfp.sh", [route("busctl", "GetCalls", exit=1)], ["call_state_query_succeeded=no", "call_objects_present=unknown"], 0),
        ("probe-hfp.sh", [route("busctl", "GetCalls", 'a(oa{sv}) 1 "/org/pipewire/Telephony/ag0/call0" 0')], ["call_objects_present=yes"], 0),
        ("probe-hfp.sh", [route("pw-dump", stdout="[]")], ["pipewire_bluez_device_present=no"], 0),
        ("probe-hfp.sh", [route("pw-dump", exit=1)], ["pipewire_bluez_device_present=unknown"], 0),
        ("probe-hfp-call.sh", [route("busctl", "introspect", "HangupAll")], ["call_control_api_available=no"], 1),
        ("probe-hfp-call.sh", [route("busctl", "introspect", exit=1)], ["call_control_api_available=no"], 1),
        ("probe-hfp-audio.sh", [route("busctl", "introspect", exit=1)], ["transport_interface_available=no"], 1),
        ("probe-hfp-audio.sh", [route("busctl", "introspect", "org.other")], ["transport_interface_available=no"], 1),
        ("probe-hfp-audio.sh", [route("busctl", "introspect", "org.pipewire.Telephony.AudioGatewayTransport1")], ["transport_activate_api_available=no"], 0),
    ])], check)
add_cases(RemainingProbeContracts, "N7", "optional_hfp_tool_missing", [
    ("tool_" + tool.replace("-", "_"), ("probe-hfp.sh", (), {}, [], {}, (tool,), [field], 0))
    for tool, field in (("systemctl", "pipewire_service_active=no"), ("pipewire", "pipewire_version=unavailable"),
                        ("wireplumber", "wireplumber_version=unavailable"), ("pw-dump", "pipewire_bluez_device_present=unknown"))], check)

add_cases(RemainingProbeContracts, "N3", "sco_initial_state_unavailable", [
    ("failed_state_read", ("probe-hfp-sco.sh", (), {}, [route("busctl", "get-property.*State", exit=1)], {}, (), ["transport_state_initial=unknown", "probe_complete=preflight"], 0)),
    ("corrupt_codec", ("probe-hfp-audio.sh", (), {}, [route("busctl", "Codec", "PRIVATE_CONTACT")], {}, (), ["transport_codec_id=unknown", "probe_complete=inconclusive"], 0)),
], check)

add_cases(RemainingProbeContracts, "N12", "probe_temporary_storage_failed", [
    (script.replace("-", "_").replace(".", "_"), (script, (), {}, [route("mktemp", exit=1)], {}, (), [], 1))
    for script in ("probe-map-sdp.sh", "probe-hfp.sh", "probe-hfp-audio.sh", "probe-hfp-call.sh", "probe-hfp-sco.sh", "probe-audio-health.sh", "probe-audio-routing.sh")], check)

add_cases(RemainingProbeContracts, "N9", "obex_session_interrupted", [
    ("interrupt_" + script.replace("-", "_").replace(".", "_"), (script,
        ("--target", "map") if "obex-" in script else (), {},
        [route("mkfifo", signal_parent="SIGTERM")], {}, (), [], 143))
    for script in ("probe-obex-session.sh", "probe-obex-read.sh", "probe-map-send.sh", "probe-map-events.sh")], check)

add_cases(RemainingProbeContracts, "N6", "obex_wire_counts_checked", [
    ("count_" + str(index), ("probe-obex-read.sh", ("--target", target), {}, [route("busctl", method, text)], {}, (), [field + "=unknown"], 0))
    for index, (target, method, text, field) in enumerate([
        ("map", "ListFolders", "wrong 1", "map_folder_list_nonempty"),
        ("map", "ListFolders", "aa{sv} 4294967296", "map_folder_list_nonempty"),
        ("map", "ListMessages", "wrong 1", "map_message_list_nonempty"),
        ("pbap", r" List ", "wrong 1", "pbap_contact_list_nonempty"),
        ("pbap", "GetSize", "q 65536", "pbap_phonebook_nonempty"),
        ("pbap", "GetSize", "u 1", "pbap_phonebook_nonempty"),
    ])], check)
add_cases(RemainingProbeContracts, "N2", "obex_wire_maximum_accepted", [
    ("max_" + str(index), ("probe-obex-read.sh", ("--target", target), {}, [route("busctl", method, text)], {}, (), [field + "=yes"], 0))
    for index, (target, method, text, field) in enumerate([
        ("map", "ListFolders", "aa{sv} 4294967294", "map_folder_list_nonempty"),
        ("map", "ListFolders", "aa{sv} 4294967295", "map_folder_list_nonempty"),
        ("pbap", "GetSize", "q 65534", "pbap_phonebook_nonempty"),
    ])], check)

add_cases(RemainingProbeContracts, "N9", "diagnostic_interrupted_after_trap", [
    (script.replace("-", "_").replace(".", "_") + signal, (script, (), {},
        [route(command, match, signal_probe=signal)], {}, (), [], code))
    for signal, code in (("SIGINT", 130), ("SIGTERM", 143))
    for script, command, match in (
        ("probe-hfp.sh", "bluetoothctl", "info"),
        ("probe-hfp-audio.sh", "bluetoothctl", "info"),
        ("probe-hfp-call.sh", "bluetoothctl", "info"),
        ("probe-hfp-sco.sh", "bluetoothctl", "info"),
        ("probe-audio-health.sh", "pw-dump", ".*"),
        ("probe-audio-routing.sh", "pw-dump", ".*"),
    )], check)
add_cases(RemainingProbeContracts, "N9", "obex_int_after_trap", [
    (script.replace("-", "_").replace(".", "_"), (script,
        ("--target", "map") if "obex-" in script else (), {},
        [route("mkfifo", signal_probe="SIGINT")], {}, (), [], 130))
    for script in ("probe-obex-session.sh", "probe-obex-read.sh", "probe-map-send.sh", "probe-map-events.sh")], check)

add_cases(RemainingProbeContracts, "N9", "diagnostic_int_defaults_overridden", [
    (script.replace("-", "_").replace(".", "_") + signal, (script, (), {},
        [route(command, signal_probe=signal)], config, (), [], code))
    for signal, code in (("SIGINT", 130), ("SIGTERM", 143))
    for script, command, config in (
        ("probe-map-sdp.sh", "sdptool", {}),
        ("probe-mns.sh", "strings", {"mns_flags": []}),
    )], check)

add_cases(RemainingProbeContracts, "N6", "passive_hfp_calls_are_unknown_when_corrupt", [
    ("corrupt_" + str(index), ("probe-hfp.sh", (), {}, [route("busctl", "GetCalls", text)], {}, (), ["call_objects_present=unknown"], 0))
    for index, text in enumerate(("", "PRIVATE_CONTACT", "a(oa{sv}) 1",
        'a(oa{sv}) 1 "/org/pipewire/Telephony/ag1/call0" 0',
        'a(oa{sv}) 0 "/org/pipewire/Telephony/ag0/call0" 0',
        'a(oa{sv}) 01 "/org/pipewire/Telephony/ag0/call0" 0',
        'a(oa{sv}) 4294967296 "/org/pipewire/Telephony/ag0/call0" 0'))], check)
