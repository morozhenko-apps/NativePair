"""Bluetooth, SDP and MNS diagnostics execute against synthetic system replies."""
import itertools
import unittest

from scenarios import add_cases
from probe_harness import run_probe, route, assert_safe, commands


class DiscoveryContracts(unittest.TestCase):
    pass


def check(self, value):
    script, args, env, routes, missing, fields, expected = value
    result = run_probe(script, args=args, env=env, routes=routes, missing=missing)
    assert_safe(self, result, expected, fields)
    self.assertFalse(any(commands(result, method) for method in ("Dial", "Activate", "HangupAll", "PushMessage")))


bt_cases = [
    ("host_only", ("probe-bluetooth.sh", ("--host-only",), {}, [], (), ["probe_scope=host", "adapter_count=1", "paired_device_count=1"], 0)),
    ("no_device", ("probe-bluetooth.sh", (), {"NATIVEPAIR_DEVICE": ""}, [], (), ["probe_scope=host"], 0)),
    ("hidden_device", ("probe-bluetooth.sh", (), {}, [route("bluetoothctl", "^info", "")], (), ["device_visible=no"], 1)),
    ("legacy_paired", ("probe-bluetooth.sh", ("--host-only",), {}, [route("bluetoothctl", "^devices", exit=1)], (), ["paired_device_count=1"], 0)),
    ("no_paired", ("probe-bluetooth.sh", ("--host-only",), {}, [route("bluetoothctl", "^(devices|paired-devices)", exit=1)], (), ["paired_device_count=0"], 0)),
    ("no_adapters", ("probe-bluetooth.sh", ("--host-only",), {}, [route("bluetoothctl", "^list$", "")], (), ["adapter_count=0"], 0)),
    ("missing_bluez_host", ("probe-bluetooth.sh", ("--host-only",), {}, [], ("bluetoothctl",), ["bluez_version=unavailable", "adapter_count=0"], 0)),
    ("missing_bluez_device", ("probe-bluetooth.sh", (), {}, [], ("bluetoothctl",), ["bluetoothctl_present=no"], 1)),
]
for missing in ("busctl", "obexctl", "systemctl"):
    bt_cases.append(("optional_missing_" + missing, ("probe-bluetooth.sh", ("--host-only",), {}, [], (missing,),
                                                  ["session_dbus_available=no"] if missing == "busctl" else [], 0)))
for paired, trusted, connected in itertools.product(("yes", "no"), repeat=3):
    info = f"Name: PRIVATE_CONTACT\nPaired: {paired}\nTrusted: {trusted}\nConnected: {connected}\n"
    bt_cases.append(("properties_" + "_".join((paired, trusted, connected)), (
        "probe-bluetooth.sh", (), {}, [route("bluetoothctl", "^info", info)], (),
        [f"device_paired={paired}", f"device_trusted={trusted}", f"device_connected={connected}",
         "advertised_map_mse=no", "advertised_pbap_pse=no", "advertised_hfp_ag=no", "advertised_ancs=no"], 0)))
for name, uuid in [("map_mse", "00001132-0000-1000-8000-00805f9b34fb"),
                   ("pbap_pse", "0000112f-0000-1000-8000-00805f9b34fb"),
                   ("hfp_ag", "0000111f-0000-1000-8000-00805f9b34fb"),
                   ("ancs", "7905f431-b5ce-4e99-a40f-4b1e122d00d0")]:
    for case, value in [("lower", uuid), ("upper", uuid.upper())]:
        bt_cases.append((name + "_" + case, ("probe-bluetooth.sh", (), {},
            [route("bluetoothctl", "^info", "Name: PRIVATE_CONTACT\nUUID: " + value)], (), ["advertised_" + name + "=yes"], 0)))
for command, match, field in [("systemctl", "bluetooth.service", "bluetooth_service_active"),
                              ("systemctl", "mpris-proxy", "mpris_proxy_user_service_active"),
                              ("busctl", "list", "session_dbus_available")]:
    bt_cases.append(("service_failed_" + field, ("probe-bluetooth.sh", ("--host-only",), {},
        [route(command, match, stderr="PRIVATE_CONTACT", exit=1)], (), [field + "=no"], 0)))
add_cases(DiscoveryContracts, "Positive", "bluetooth_probed", bt_cases, check)

sdp_cases = []
for instance, types, features, mas in itertools.product((False, True), repeat=4):
    output = "PRIVATE_CONTACT\n" + "".join([
        '<attribute id="0x0315"/>' if instance else "",
        '<attribute id="0x0316"/>' if types else "",
        '<attribute id="0x0317"/>' if features else "",
        '<uuid value="0x1132"/>' if mas else ""])
    sdp_cases.append(("attributes_" + "".join(str(int(x)) for x in (instance, types, features, mas)), (
        "probe-map-sdp.sh", (), {}, [route("sdptool", stdout=output)], (), [
            "remote_sdp_query=yes", "mas_instance_id_present=" + ("yes" if instance else "no"),
            "supported_message_types_present=" + ("yes" if types else "no"),
            "map_supported_features_present=" + ("yes" if features else "no"),
            "map_mas_record_confirmed=" + ("yes" if mas else "unknown")], 0)))
for name, output in [("short_ids", '<attribute id="0x315"/><attribute id="0x316"/><attribute id="0x317"/><uuid value="00001132-0000-1000-8000-00805f9b34fb"/>'),
                      ("uppercase_ids", '<ATTRIBUTE id="0X0315"/><ATTRIBUTE id="0X0316"/><ATTRIBUTE id="0X0317"/><UUID value="0X1132"/>')]:
    sdp_cases.append((name, ("probe-map-sdp.sh", (), {}, [route("sdptool", stdout=output)], (),
                            ["mas_instance_id_present=yes", "supported_message_types_present=yes",
                             "map_supported_features_present=yes", "map_mas_record_confirmed=yes"], 0)))
add_cases(DiscoveryContracts, "Positive", "sdp_classified", sdp_cases, check)
add_cases(DiscoveryContracts, "N3", "sdp_failed", [
    ("timeout", ("probe-map-sdp.sh", (), {}, [route("timeout", stdout="PRIVATE_CONTACT", exit=124)], (),
                  ["remote_sdp_error=timeout"], 1)),
    ("query_failure", ("probe-map-sdp.sh", (), {}, [route("sdptool", stdout="PRIVATE_CONTACT", exit=1)], (),
                        ["remote_sdp_error=query_failed"], 1)),
], check)

mns_cases = [
    ("no_process", ("probe-mns.sh", (), {}, [], (), ["obexd_process_running=no", "mns_explicitly_disabled=unknown",
                        "mns_server_compiled=unknown", "controller_mns_uuid_visible=yes", "known_bluez_2315_pattern=no"], 0)),
    ("empty_local_sdp", ("probe-mns.sh", (), {}, [route("sdptool", stdout="")], (), ["local_mns_sdp_record_present=no"], 0)),
]
for missing in ("bluetoothctl", "busctl", "sdptool", "strings", "dpkg-query"):
    fields = {"bluetoothctl": "controller_mns_uuid_visible=no", "busctl": "obex_service_available=no",
              "sdptool": "local_sdp_error_class=tool_missing", "strings": "strings_present=no",
              "dpkg-query": "bluez_obexd_package_version=unknown"}
    mns_cases.append(("missing_" + missing.replace("-", "_"), ("probe-mns.sh", (), {}, [], (missing,), [fields[missing]], 0)))
for output, classification in [("Permission denied PRIVATE_CONTACT", "permission"),
                                ("not permitted PRIVATE_CONTACT", "permission"),
                                ("access denied PRIVATE_CONTACT", "permission"),
                                ("Connection refused PRIVATE_CONTACT", "service_unavailable"),
                                ("failed to connect PRIVATE_CONTACT", "service_unavailable"),
                                ("no such file PRIVATE_CONTACT", "service_unavailable"),
                                ("not available PRIVATE_CONTACT", "service_unavailable"),
                                ("not found PRIVATE_CONTACT", "service_unavailable"),
                                ("PRIVATE_CONTACT", "unknown")]:
    mns_cases.append(("sdp_error_" + str(len(mns_cases)), ("probe-mns.sh", (), {}, [route("sdptool", stdout=output, exit=1)], (),
        ["local_sdp_query=no", "local_sdp_error_class=" + classification, "local_mns_sdp_record_present=unknown"], 0)))
for uuid in ("Message Notification", "0x1133", "00001133-0000-1000-8000-00805f9b34fb"):
    mns_cases.append(("sdp_mns_" + str(len(mns_cases)), ("probe-mns.sh", (), {}, [route("sdptool", stdout=uuid)], (),
        ["local_sdp_query=yes", "local_sdp_error_class=none", "local_mns_sdp_record_present=yes"], 0)))
for command, match, field in [("busctl", "list", "obex_service_available=no"),
                              ("busctl", "introspect", "profile_manager_available=no"),
                              ("bluetoothctl", "show", "controller_mns_uuid_visible=no")]:
    mns_cases.append(("service_failure_" + command + match, ("probe-mns.sh", (), {}, [route(command, match, exit=1)], (), [field], 0)))
add_cases(DiscoveryContracts, "N3", "mns_classified", mns_cases, check)
