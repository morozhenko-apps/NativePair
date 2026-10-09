"""MNS plugin and compilation inspection on an exclusively owned fake process."""
import itertools
import unittest

from scenarios import add_cases
from probe_harness import run_probe, route, assert_safe


class MnsProcessContracts(unittest.TestCase):
    pass


def check(self, value):
    config, routes, fields = value
    result = run_probe("probe-mns.sh", config=config, routes=routes)
    assert_safe(self, result, fields=fields)


cases = []
for client, event, name, visible in itertools.product((False, True), repeat=4):
    text = "\n".join(value for flag, value in [
        (client, "x-bt/MAP-NotificationRegistration"),
        (event, "x-bt/MAP-event-report"), (name, "Message Notification server")]
        if flag)
    cases.append(("signatures_" + "".join(str(int(value)) for value in (client, event, name, visible)), (
        {"mns_flags": [], "strings": text}, [] if visible else [route("bluetoothctl", "show", "")],
        ["obexd_process_running=yes", "mns_explicitly_disabled=no",
         "obexd_map_client_signature=" + ("yes" if client else "no"),
         "obexd_mns_event_report_signature=" + ("yes" if event else "no"),
         "obexd_mns_name_signature=" + ("yes" if name else "no"),
         "mns_server_compiled=" + ("likely_yes" if event or name else "likely_no"),
         "known_bluez_2315_pattern=" + ("yes" if client and event and not visible else "no")]
    )))
add_cases(MnsProcessContracts, "Positive", "compiled_profiles_classified", cases, check)

add_cases(MnsProcessContracts, "N7", "disabled_plugin_classified", [
    ("flags_" + str(index), ({"mns_flags": flags}, [route("bluetoothctl", "show", "")],
        ["mns_explicitly_disabled=" + ("yes" if disabled else "no"),
         "known_bluez_2315_pattern=" + ("no" if disabled else "yes")]))
    for index, (flags, disabled) in enumerate([
        (["--noplugin=mns"], True), (["--noplugin", "mns"], True),
        (["--noplugin=map,mns"], True), (["--noplugin=mns,map"], True),
        (["--noplugin=map,pbap,mns"], True), (["--noplugin=amns"], False),
        (["--noplugin=mns2"], False), (["--noplugin=map"], False),
    ])], check)
