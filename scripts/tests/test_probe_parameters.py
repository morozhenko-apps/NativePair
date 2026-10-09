"""Every existing probe's parameter and missing-dependency contracts."""
import unittest

from scenarios import add_cases
from probe_harness import run_probe, assert_safe, route

DEPENDENCIES = {
    "probe-obex-session.sh": "busctl bluetoothctl obexctl stdbuf mktemp",
    "probe-obex-read.sh": "busctl bluetoothctl obexctl stdbuf mktemp",
    "probe-map-send.sh": "busctl bluetoothctl obexctl stdbuf mktemp wc tail grep sed od tr python3",
    "probe-map-events.sh": "busctl bluetoothctl obexctl stdbuf mktemp",
    "probe-map-sdp.sh": "sdptool timeout mktemp",
    "probe-hfp.sh": "bluetoothctl busctl grep awk sed head tail tr mktemp timeout seq sleep",
    "probe-hfp-audio.sh": "bluetoothctl busctl grep head mktemp sed seq sleep timeout",
    "probe-hfp-call.sh": "bluetoothctl busctl grep head mktemp sleep seq timeout",
    "probe-hfp-sco.sh": "bluetoothctl busctl cat grep head mktemp python3 pw-dump sed seq sleep timeout wpctl",
    "probe-audio-routing.sh": "busctl grep head mktemp python3 pw-dump sed wpctl",
    "probe-audio-health.sh": "grep journalctl mktemp pw-dump python3 pw-top sed systemctl timeout wpctl",
}
TARGETS = {"probe-obex-session.sh", "probe-obex-read.sh"}
DEVICE_SCRIPTS = tuple(name for name in DEPENDENCIES if name != "probe-audio-health.sh") + ("probe-bluetooth.sh",)
HELP_SCRIPTS = tuple(name for name in DEPENDENCIES if name not in
                     ("probe-audio-health.sh", "probe-audio-routing.sh")) + ("probe-bluetooth.sh",)
TIMERS = {
    "probe-obex-session.sh": ("NATIVEPAIR_OBEX_TIMEOUT",),
    "probe-obex-read.sh": ("NATIVEPAIR_OBEX_TIMEOUT",),
    "probe-map-send.sh": ("NATIVEPAIR_OBEX_TIMEOUT", "NATIVEPAIR_SEND_TIMEOUT"),
    "probe-map-events.sh": ("NATIVEPAIR_OBEX_TIMEOUT", "NATIVEPAIR_EVENT_TIMEOUT"),
    "probe-hfp.sh": ("NATIVEPAIR_HFP_CONNECT_TIMEOUT",),
    "probe-hfp-audio.sh": ("NATIVEPAIR_HFP_CONNECT_TIMEOUT",),
    "probe-hfp-call.sh": ("NATIVEPAIR_CALL_OBSERVE_SECONDS",),
    "probe-hfp-sco.sh": ("NATIVEPAIR_HFP_CONNECT_TIMEOUT", "NATIVEPAIR_SCO_STATE_TIMEOUT",
                          "NATIVEPAIR_CALL_ACTIVE_TIMEOUT", "NATIVEPAIR_SCO_HUMAN_WINDOW"),
}


def arguments(script):
    return ("--target", "map") if script in TARGETS else ()


class ParameterContracts(unittest.TestCase):
    pass


def check(self, value):
    script, args, env, missing, expected, fields = value
    result = run_probe(script, args=args, env=env, missing=missing)
    assert_safe(self, result, expected, fields)
    self.assertFalse(any(cmd for cmd in result.state["commands"]
                         if any(method in cmd for method in ("Dial", "HangupAll", "Activate", "PushMessage"))))


add_cases(ParameterContracts, "Positive", "help_requested", [
    (name.replace("-", "_").replace(".", "_") + "_" + str(index),
     (name, (flag,), {"NATIVEPAIR_DEVICE": "bad"}, (), 0, ()))
    for name in HELP_SCRIPTS for index, flag in enumerate(("--help", "-h"))], check)

add_cases(ParameterContracts, "N1", "address_validated", [
    (name.replace("-", "_").replace(".", "_") + "_address_" + str(index),
     (name, arguments(name), {"NATIVEPAIR_DEVICE": address}, (), 2, ()))
    for name in DEVICE_SCRIPTS
    for index, address in enumerate(("bad", "02:00:00:00:00", "02:00:00:00:00:000",
                                     "GG:00:00:00:00:00", " 02:00:00:00:00:01", "02-00-00-00-00-01"))], check)

add_cases(ParameterContracts, "N1", "timeout_validated", [
    (name.replace("-", "_").replace(".", "_") + "_" + variable.lower() + "_" + str(index),
     (name, arguments(name), {variable: text}, (), 2, ()))
    for name, variables in TIMERS.items() for variable in variables
    for index, text in enumerate(("0", "-1", "01", "1.5", "NaN", "Infinity", " 1", "1s"))], check)

add_cases(ParameterContracts, "N7", "dependency_missing", [
    (name.replace("-", "_").replace(".", "_") + "_missing_" + dependency.replace("-", "_"),
     (name, arguments(name), {}, (dependency,), 1, ()))
    for name, dependencies in DEPENDENCIES.items() for dependency in dependencies.split()], check)

add_cases(ParameterContracts, "N1", "unknown_argument_rejected", [
    (name.replace("-", "_").replace(".", "_"), (name, ("--unknown",), {}, (), 2, ()))
    for name in HELP_SCRIPTS], check)

add_cases(ParameterContracts, "N1", "target_validated", [
    (name.replace("-", "_").replace(".", "_") + "_target_" + str(index),
     (name, args, {}, (), 2, ()))
    for name in TARGETS for index, args in enumerate(((), ("--target",),
        ("--target", "invalid"), ("--target", "MAP"), ("--device",)))], check)

add_cases(ParameterContracts, "N1", "bluetooth_address_argument_missing", [
    ("missing_device_value", ("probe-bluetooth.sh", ("--device",), {}, (), 2, ()))], check)

add_cases(ParameterContracts, "N1", "sms_recipient_validated", [
    ("sms_recipient_" + str(index), ("probe-map-send.sh", (),
        {"NATIVEPAIR_SMS_RECIPIENT": text}, (), 2, ()))
    for index, text in enumerate(("", "15551234567", "+01234567", "+123456", "+1234567890123456",
                                  "+123 4567", "+123456x", "NaN"))], check)

add_cases(ParameterContracts, "N1", "dial_recipient_validated", [
    (name.replace("-", "_").replace(".", "_") + "_recipient_" + str(index),
     (name, ("--dial",), {"NATIVEPAIR_CALL_RECIPIENT": text}, (), 2, ()))
    for name in ("probe-hfp-call.sh", "probe-hfp-sco.sh")
    for index, text in enumerate(("", "1" * 81, "E", "a", "12 34", "1;2", "NaN"))], check)

add_cases(ParameterContracts, "N2", "health_iterations_validated", [
    ("health_iteration_" + str(index), ("probe-audio-health.sh", (),
        {"NATIVEPAIR_AUDIO_HEALTH_ITERATIONS": text}, (), 2, ()))
    for index, text in enumerate(("0", "1", "61", "-1", "2.5", "NaN", "Infinity", "text"))], check)

add_cases(ParameterContracts, "N10", "private_argument_rejected", [
    (name.replace("-", "_").replace(".", "_"),
     (name, ("PRIVATE_CONTACT",), {}, (), 2, ()))
    for name in HELP_SCRIPTS], check)
