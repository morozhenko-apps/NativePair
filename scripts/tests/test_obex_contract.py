"""MAP/PBAP session lifetime, bounded read, error and cleanup contracts."""
import unittest

from scenarios import add_cases, category
from probe_harness import run_probe, route, assert_safe, commands

SESSION = "probe-obex-session.sh"
READ = "probe-obex-read.sh"
OBEX_SCRIPTS = (SESSION, READ, "probe-map-send.sh", "probe-map-events.sh")


class ObexContracts(unittest.TestCase):
    @category("Positive")
    def test_given_map_when_read_requested_then_only_bounded_allowlisted_fields_are_requested(self):
        result = run_probe(READ, args=("--target", "map"))
        assert_safe(self, result, fields=("read_probe_complete=yes", "map_message_list_nonempty=yes"))
        self.assertEqual(commands(result, "ListFolders")[0][-5:], ["a{sv}", "1", "MaxCount", "q", "16"])
        self.assertEqual(commands(result, "ListMessages")[0][-10:],
                         ["sa{sv}", "inbox", "2", "MaxCount", "q", "1", "Fields", "as", "1", "type"])
        self.assertEqual(len(commands(result, "ListMessages")), 1)

    @category("Positive")
    def test_given_pbap_when_read_requested_then_only_one_contact_is_requested(self):
        result = run_probe(READ, args=("--target", "pbap"))
        assert_safe(self, result, fields=("read_probe_complete=yes", "pbap_contact_list_nonempty=yes"))
        self.assertEqual(commands(result, "Select")[0][-3:], ["ss", "int", "pb"])
        self.assertEqual(commands(result, "List")[0][-5:], ["a{sv}", "1", "MaxCount", "q", "1"])
        self.assertEqual(len(commands(result, "List")), 1)


def check(self, value):
    script, target, routes, config, fields, expected = value
    args = ("--target", target) if script in (SESSION, READ) else ()
    result = run_probe(script, args=args, routes=routes, config=config)
    assert_safe(self, result, expected, fields)
    self.assertFalse(any(commands(result, method) for method in ("Dial", "Activate", "HangupAll", "PushMessage")))


cases = []
for script in OBEX_SCRIPTS:
    for name, routes, config, fields, expected in [
        ("service_absent", [route("busctl", "list", "org.other 1")], {}, ["obex_service_available=no"], 1),
        ("service_error", [route("busctl", "list", "PRIVATE_CONTACT", exit=1)], {}, ["obex_service_available=no"], 1),
        ("unpaired", [route("bluetoothctl", "info", "Paired: no\nPRIVATE_CONTACT")], {}, ["device_paired=no"], 1),
        ("device_query_failed", [route("bluetoothctl", "info", exit=1)], {}, ["device_paired=no"], 1),
        ("not_ready", [], {"obex_ready": "PRIVATE_CONTACT"}, ["obexctl_ready=no"], 1),
        ("connect_timeout", [], {"obex_connect": "PRIVATE_CONTACT"}, [], 1),
        ("connect_error", [], {"obex_connect": "Failed to connect PRIVATE_CONTACT +15551234567"}, [], 1),
        ("missing_session", [], {"obex_connect": "Connection successful\n[NEW] MessageAccess"}, [], 1),
    ]:
        cases.append((script.replace("-", "_").replace(".", "_") + "_" + name,
                      (script, "map", routes, config, fields, expected)))
add_cases(ObexContracts, "N3", "session_fails_cleanly", cases, check)

add_cases(ObexContracts, "Positive", "session_created", [
    ("map", (SESSION, "map", [], {}, ["session_established=yes", "session_target_matches=yes"], 0)),
    ("pbap", (SESSION, "pbap", [route("busctl", "get-property.*Target", 's "0000112f-0000-1000-8000-00805f9b34fb"')], {},
              ["session_established=yes", "session_target_matches=yes"], 0)),
    ("optional_proxy_absent", (SESSION, "map", [], {"obex_connect": "Connection successful\nSession /org/bluez/obex/client/session0"},
                              ["target_proxy_observed=no", "session_established=yes"], 0)),
], check)

add_cases(ObexContracts, "N6", "session_interfaces_checked", [
    ("session_interface_absent", (SESSION, "map", [route("busctl", "introspect.*Session1", exit=1)], {}, ["session_interface_present=no"], 1)),
    ("target_interface_absent", (SESSION, "map", [route("busctl", "introspect.*MessageAccess1", exit=1)], {}, ["session_established=no"], 1)),
    ("target_property_unavailable", (SESSION, "map", [route("busctl", "get-property.*Target", exit=1)], {}, ["session_target_uuid=unavailable", "session_target_matches=no"], 0)),
    ("target_property_corrupt", (SESSION, "map", [route("busctl", "get-property.*Target", 's "PRIVATE_CONTACT"')], {}, ["session_target_uuid=unknown", "session_target_matches=no"], 0)),
    ("target_property_mismatch", (SESSION, "map", [route("busctl", "get-property.*Target", 's "0000112f-0000-1000-8000-00805f9b34fb"')], {}, ["session_target_matches=no"], 0)),
    ("read_interface_absent", (READ, "map", [route("busctl", "introspect", exit=1)], {}, ["session_error=target_interface_missing"], 1)),
    ("read_proxy_absent", (READ, "map", [], {"obex_connect": "Connection successful\nSession /org/bluez/obex/client/session0"}, ["session_error=target_proxy_missing"], 1)),
], check)

read_failures = []
for target, method, match, field in [
    ("map", "folders", "ListFolders", "map_folders"),
    ("map", "telecom", "SetFolder s telecom", "map_telecom"),
    ("map", "msg", "SetFolder s msg", "map_msg"),
    ("map", "messages", "ListMessages", "map_messages"),
    ("pbap", "select", "Select", "pbap_select"),
    ("pbap", "size", "GetSize", "pbap_size"),
    ("pbap", "list", r" List ", "pbap_list"),
]:
    for error in ("org.bluez.obex.Error.NotAuthorized", "PRIVATE_CONTACT"):
        read_failures.append((target + "_" + method + "_" + str(len(read_failures)), (
            READ, target, [route("busctl", match, error + " PRIVATE_CONTACT", exit=1)], {},
            [field + "_error=" + (error if error.startswith("org.") else "unknown")], 1)))
add_cases(ObexContracts, "N7", "read_operation_rejected", read_failures, check)

arrays = []
for target, match, field, signature in [("map", "ListFolders", "map_folder", "aa{sv}"),
                                      ("map", "ListMessages", "map_message", "a{oa{sv}}"),
                                      ("pbap", r" List ", "pbap_contact", "a(ss)")]:
    for label, output, expected in [("zero", signature + " 0", "no"),
                                    ("one", signature + " 1 PRIVATE_CONTACT", "yes"),
                                    ("two", signature + " 2 PRIVATE_CONTACT", "yes"),
                                    ("empty", "", "unknown"),
                                    ("malformed", "PRIVATE_CONTACT", "unknown"),
                                    ("invalid_count", signature + " x", "unknown"),
                                    ("negative_count", signature + " -1", "unknown"),
                                    ("large_count", signature + " 999999999999999999999999999", "unknown")]:
        arrays.append((target + "_" + field + "_" + label, (READ, target,
            [route("busctl", match, output)], {}, [field + "_list_nonempty=" + expected, "read_probe_complete=yes"], 0)))
add_cases(ObexContracts, "N2", "array_count_classified", arrays, check)
add_cases(ObexContracts, "N6", "phonebook_size_classified", [
    ("phonebook_" + name, (READ, "pbap", [route("busctl", "GetSize", text)], {},
                          ["pbap_phonebook_nonempty=" + expected], 0))
    for name, text, expected in [("empty", "q 0", "no"), ("one", "q 1", "yes"),
                                 ("max", "q 65535", "yes"), ("corrupt", "PRIVATE_CONTACT", "unknown"),
                                 ("missing", "", "unknown"), ("negative", "q -1", "unknown"),
                                 ("overflow", "q 999999999999999999999999999", "unknown")]], check)

add_cases(ObexContracts, "N12", "fifo_creation_fails", [
    (script.replace("-", "_").replace(".", "_"), (script, "map", [route("mkfifo", exit=1)], {}, [], 1))
    for script in OBEX_SCRIPTS], check)

add_cases(ObexContracts, "N12", "temporary_creation_fails", [
    (script.replace("-", "_").replace(".", "_"), (script, "map", [route("mktemp", exit=1)], {}, [], 1))
    for script in OBEX_SCRIPTS], check)
