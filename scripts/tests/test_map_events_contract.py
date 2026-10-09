"""MAP event generation, session correlation, replay suppression and death."""
import contextlib
import io
from pathlib import Path
import tempfile
import unittest

from scenarios import add_cases
from probe_harness import run_probe, route, assert_safe, commands
from test_obex_monitor import event, monitor

SESSION = "/org/bluez/obex/client/session0"


def message(index=0, session=SESSION, removed=False):
    member = "InterfacesRemoved" if removed else "InterfacesAdded"
    return (f'‣ Type=signal\n  Path={session} Interface=org.freedesktop.DBus.ObjectManager Member={member}\n'
            f'  OBJECT_PATH "{session}/message{index}";\n  STRING "org.bluez.obex.Message1";\n')


class EventParserContracts(unittest.TestCase):
    pass


def count(self, value):
    text, session, obex, expected = value
    self.assertEqual(monitor.message_count(text, session, obex), expected)


add_cases(EventParserContracts, "N4", "message_counted", [
    ("empty", ("", SESSION, False, 0)),
    ("new", (message(), SESSION, False, 1)),
    ("duplicate", (message() * 2, SESSION, False, 1)),
    ("different_objects", (message() + message(1), SESSION, False, 2)),
    ("removed_readded", (message() + message(removed=True) + message(), SESSION, False, 2)),
    ("remove_unknown", (message(removed=True), SESSION, False, 0)),
    ("other_session", (message(session=SESSION + "1"), SESSION, False, 0)),
    ("invalid_session", (message(), "PRIVATE_CONTACT", False, 0)),
    ("changed_not_added", (message().replace("InterfacesAdded", "PropertiesChanged"), SESSION, False, 0)),
    ("method_not_signal", (message().replace("Type=signal", "Type=method_return"), SESSION, False, 0)),
    ("wrong_dbus_interface", (message().replace("org.freedesktop.DBus.ObjectManager", "org.other"), SESSION, False, 0)),
    ("missing_dbus_interface", (message().replace("Interface=", "Other="), SESSION, False, 0)),
    ("other_interface", (message().replace("Message1", "Session1"), SESSION, False, 0)),
    ("wrong_object_suffix", (message().replace("/message0\"", "/message0secret\""), SESSION, False, 0)),
    ("obex_new", (f"[NEW] Message {SESSION}/message0\n", SESSION, True, 1)),
    ("obex_duplicate", (f"[NEW] Message {SESSION}/message0\n" * 2, SESSION, True, 1)),
    ("obex_remove_readd", (f"[NEW] Message {SESSION}/message0\n[DEL] Message {SESSION}/message0\n[NEW] Message {SESSION}/message0\n", SESSION, True, 2)),
    ("obex_other_session", (f"[NEW] Message {SESSION}1/message0\n", SESSION, True, 0)),
    ("obex_wrong_suffix", (f"[NEW] Message {SESSION}/message0private\n", SESSION, True, 0)),
], count)


def registration(self, value):
    text, session, expected = value
    self.assertEqual(monitor.registration(text, session), expected)


add_cases(EventParserContracts, "N6", "registration_correlated", [
    ("none", ("", SESSION, "no not_seen")),
    ("invalid_session", (event(), "PRIVATE_CONTACT", "no not_seen")),
    ("complete", (event(), SESSION, "yes complete")),
    ("error", (event(state="error"), SESSION, "yes error")),
    ("pending", (event(state="queued"), SESSION, "yes unknown")),
    ("other_session", (event(path=SESSION + "1/transfer0"), SESSION, "no not_seen")),
    ("created", (f'‣ Type=signal\nInterface=org.freedesktop.DBus.ObjectManager Member=InterfacesAdded\nOBJECT_PATH "{SESSION}/transfer0";\nSTRING "org.bluez.obex.Transfer1";', SESSION, "yes unknown")),
    ("method_return", (event(kind="method_return"), SESSION, "no not_seen")),
    ("wrong_interface", (event(interface="org.other"), SESSION, "no not_seen")),
    ("wrong_member", (event(member="Other"), SESSION, "no not_seen")),
    ("no_transfer_interface", (event(transfer="org.other"), SESSION, "no not_seen")),
    ("removed", (f'‣ Type=signal\nInterface=org.freedesktop.DBus.ObjectManager Member=InterfacesRemoved\nOBJECT_PATH "{SESSION}/transfer0";\nSTRING "org.bluez.obex.Transfer1";', SESSION, "no not_seen")),
    ("complete_and_error", (event() + event(state="error"), SESSION, "yes error")),
], registration)


def cli(self, value):
    mode, text, expected = value
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "stream.log"
        path.write_text(text)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = monitor.main([mode, str(path), SESSION])
    self.assertEqual(code, 0)
    self.assertEqual(output.getvalue(), expected + "\n")


add_cases(EventParserContracts, "Positive", "monitor_mode_invoked", [
    ("messages", ("--messages", message(), "1")),
    ("obex_messages", ("--obex-messages", f"[NEW] Message {SESSION}/message0\n", "1")),
    ("registration", ("--registration", event(), "yes complete")),
], cli)


class MapEventContracts(unittest.TestCase):
    pass


def contract(self, value):
    config, routes, fields, code = value
    result = run_probe("probe-map-events.sh", config=config, routes=routes)
    assert_safe(self, result, code, fields)
    self.assertEqual(commands(result, "PushMessage"), [])
    self.assertEqual(commands(result, "Dial"), [])


def injection(content, mode="--messages", filename="busctl-monitor.log", kill=None):
    return route("python3", mode, replies=[{"delegate": True}, {
        "delegate": True, "append": filename, "content": content, "kill": kill or []}])


event_cases = []
for name, registration_text, expected in [("complete", event(), "complete"),
                                          ("error", event(state="error"), "error"),
                                          ("unknown", event(state="queued"), "unknown"),
                                          ("not_seen", "", "not_seen")]:
    for source in ("monitor", "obex"):
        route_ = injection(message()) if source == "monitor" else injection(
            f"[NEW] Message {SESSION}/message0\n", "--obex-messages", "obexctl.log")
        event_cases.append((name + "_" + source, ({"registration": registration_text}, [route_],
            ["notification_registration_status=" + expected, "map_event_observed=yes",
             "notification_registration_effective=yes", "event_probe_complete=yes"], 0)))
add_cases(MapEventContracts, "Positive", "incoming_event_observed", event_cases, contract)
add_cases(MapEventContracts, "N4", "replayed_event_ignored", [
    ("existing_monitor_object", ({"registration": message()}, [injection(message())],
        ["map_event_observed=no", "event_probe_complete=inconclusive"], 0)),
    ("other_session_monitor_object", ({}, [injection(message(session=SESSION + "1"))],
        ["map_event_observed=no", "event_probe_complete=inconclusive"], 0)),
    ("remove_readd_object", ({"registration": message()}, [injection(message(removed=True) + message())],
        ["map_event_observed=yes", "event_probe_complete=yes"], 0)),
], contract)
add_cases(MapEventContracts, "N3", "event_sources_exited", [
    (name, ({}, [injection("", kill=[name])], ["event_error=" + error, "event_probe_complete=no"], 1))
    for name, error in (("obexctl", "obexctl_exited"), ("busctl_monitor", "dbus_monitor_exited"))], contract)
add_cases(MapEventContracts, "N2", "event_window_empty", [
    ("registration_complete", ({"registration": event()}, [], ["event_probe_complete=inconclusive", "notification_registration_status=complete"], 0)),
    ("no_registration", ({}, [], ["event_probe_complete=inconclusive", "notification_registration_status=not_seen"], 0)),
], contract)
