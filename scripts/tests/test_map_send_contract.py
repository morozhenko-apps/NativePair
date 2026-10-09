"""One-shot MAP sends, generated bMessage and correlated transfer evidence."""
import unittest

from scenarios import add_cases, category
from probe_harness import run_probe, route, assert_safe, commands, NUMBER
from test_obex_monitor import event, PATH

SEND = "probe-map-send.sh"


class SendContracts(unittest.TestCase):
    @category("Positive")
    def test_given_preflight_when_bmessage_prepared_then_private_crlf_framing_and_length_are_exact(self):
        result = run_probe(SEND, config={"capture_payload": True})
        assert_safe(self, result, fields=("actual_send=no", "bmessage_structure_valid=yes", "send_probe_complete=preflight"))
        self.assertEqual(commands(result, "PushMessage"), [])
        self.assertEqual(result.state["payload_mode"], 0o600)
        payload = bytes.fromhex(result.state["payload"])
        body = b"BEGIN:MSG\r\nNativePair MAP send probe\r\nEND:MSG\r\n"
        self.assertIn(b"LENGTH:" + str(len(body)).encode() + b"\r\n" + body, payload)
        self.assertTrue(payload.endswith(b"END:BBODY\r\nEND:BENV\r\nEND:BMSG\r\n"))
        self.assertIn(b"TEL:" + NUMBER.encode() + b"\r\n", payload)
        self.assertNotIn(b"\n", payload.replace(b"\r\n", b""))
        self.assertNotIn(b"\r", payload.replace(b"\r\n", b""))

    @category("N4")
    def test_given_repeated_send_flag_when_send_invoked_then_exactly_one_push_with_retry_disabled(self):
        result = run_probe(SEND, args=("--send", "--send"), config={"push_event": event()})
        assert_safe(self, result, fields=("send_probe_complete=yes", "push_transfer_status=complete"))
        pushed = commands(result, "PushMessage")
        self.assertEqual(len(pushed), 1)
        self.assertEqual(pushed[0][-11:], ["outbox", "3", "Transparent", "b", "true",
                                         "Retry", "b", "false", "Charset", "s", "utf8"])
        self.assertEqual(result.state["payload_mode"], 0o600)


def check(self, value):
    args, routes, config, env, fields, expected, pushes = value
    result = run_probe(SEND, args=args, routes=routes, config=config, env=env)
    assert_safe(self, result, expected, fields)
    self.assertEqual(len(commands(result, "PushMessage")), pushes)


add_cases(SendContracts, "N3", "send_prerequisite_rejected", [
    (name, ((), routes, {}, {}, fields, 1, 0))
    for name, routes, fields in [
        ("monitor_failure", [route("busctl", "monitor", exit=1)], ["dbus_monitor_ready=no"]),
        ("unsupported_type", [route("busctl", "SupportedTypes", 'as 1 "MMS"')], ["sms_gsm_supported=no"]),
        ("supported_types_failure", [route("busctl", "SupportedTypes", stderr="PRIVATE_CONTACT", exit=1)], ["sms_gsm_supported=no"]),
        ("telecom_failure", [route("busctl", "SetFolder s telecom", exit=1)], ["map_telecom_selected=no"]),
        ("message_folder_failure", [route("busctl", "SetFolder s msg", exit=1)], ["map_msg_selected=no"]),
    ]], check)

add_cases(SendContracts, "N5", "transfer_evidence_correlated", [
    (name, (("--send",), [], config, {}, fields, expected, 1))
    for name, config, fields, expected in [
        ("matching_complete", {"push_event": event()}, ["push_transfer_status=complete", "send_probe_complete=yes"], 0),
        ("matching_error", {"push_event": event(state="error")}, ["push_transfer_status=error", "send_error=transfer_error"], 1),
        ("unrelated_complete", {"push_event": event(path=PATH + "1")}, ["push_transfer_status=unknown", "send_probe_complete=inconclusive"], 0),
        ("unrelated_error", {"push_event": event(path=PATH + "1", state="error")}, ["push_transfer_status=unknown", "send_probe_complete=inconclusive"], 0),
        ("unrelated_then_matching", {"push_event": event(path=PATH + "1", state="error") + event()}, ["send_probe_complete=yes"], 0),
        ("matching_then_unrelated", {"push_event": event(state="error") + event(path=PATH + "1")}, ["send_error=transfer_error"], 1),
        ("no_status", {}, ["send_probe_complete=inconclusive"], 0),
        ("registration_replay", {"registration": event()}, ["send_probe_complete=inconclusive"], 0),
    ]], check)

add_cases(SendContracts, "N3", "ambiguous_push_not_retried", [
    ("push_failure", (("--send",), [route("busctl", "PushMessage", "PRIVATE_CONTACT", exit=1)], {}, {},
                      ["push_message_accepted=no", "send_error=push_message_call_failed"], 1, 1)),
    ("session_lost", (("--send",), [route("busctl", "PushMessage", 'oa{sv} "' + PATH + '" 0', kill=["obexctl"])], {}, {},
                      ["send_error=session_lost"], 1, 1)),
], check)

add_cases(SendContracts, "N6", "missing_transfer_cannot_confirm_send", [
    ("path_" + str(index), (("--send",), [route("busctl", "PushMessage", response)], {"push_event": event()}, {},
                           ["send_probe_complete=inconclusive"], 0, 1))
    for index, response in enumerate(("", "PRIVATE_CONTACT", 'oa{sv} "PRIVATE_CONTACT" 0',
                                      'oa{sv} "' + PATH + 'x" 0'))], check)

add_cases(SendContracts, "N2", "recipient_boundary_accepted", [
    ("recipient_length_" + str(length), ((), [], {}, {"NATIVEPAIR_SMS_RECIPIENT": "+" + "1" * length},
                                        ["send_probe_complete=preflight"], 0, 0))
    for length in (7, 8, 14, 15)], check)

add_cases(SendContracts, "N12", "payload_write_failure_stops_send", [
    ("private_mode_failed", (("--send",), [route("chmod", exit=1)], {}, {}, [], 1, 0)),
], check)
