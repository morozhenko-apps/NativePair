"""Correlated OBEX monitor parsing: synthetic busctl message framing only."""
import contextlib
import io
from pathlib import Path
import sys
import tempfile
import unittest

from scenarios import add_cases, category

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import probe_obex_monitor as monitor

PATH = "/org/bluez/obex/client/session0/transfer0"


def event(path=PATH, state="complete", kind="signal", interface="org.freedesktop.DBus.Properties",
          member="PropertiesChanged", transfer="org.bluez.obex.Transfer1", key="Status", signature="s"):
    return (f'‣ Type={kind} Endian=l\n  Path={path} Interface={interface} Member={member}\n'
            f'  MESSAGE "sa{{sv}}as" {{\n    STRING "{transfer}";\n    ARRAY "{{sv}}" {{\n'
            f'      DICT_ENTRY "sv" {{\n        STRING "{key}";\n        VARIANT "{signature}" {{\n'
            f'          STRING "{state}";\n        }};\n      }};\n    }};\n  }};\n')


class MonitorContracts(unittest.TestCase):
    @category("N12")
    def test_given_missing_log_when_parser_invoked_then_unknown_without_path_disclosure(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = monitor.main(["/missing/PRIVATE_CONTACT", PATH])
        self.assertEqual(code, 1)
        self.assertEqual(output.getvalue(), "unknown\n")

    @category("Positive")
    def test_given_valid_log_when_parser_invoked_then_only_enum_emitted(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "monitor.log"
            path.write_text(event())
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = monitor.main([str(path), PATH])
        self.assertEqual(code, 0)
        self.assertEqual(output.getvalue(), "complete\n")


def check(self, value):
    text, path, expected = value
    self.assertEqual(monitor.transfer_status(text, path), expected)


add_cases(MonitorContracts, "Positive", "transfer_correlated", [
    ("complete", (event(), PATH, "complete")),
    ("error", (event(state="error"), PATH, "error")),
    ("duplicate_complete", (event() * 2, PATH, "complete")),
    ("error_after_complete", (event() + event(state="error"), PATH, "error")),
    ("complete_after_error", (event(state="error") + event(), PATH, "error")),
    ("unrelated_then_matching", (event(path=PATH + "1") + event(), PATH, "complete")),
], check)
add_cases(MonitorContracts, "N6", "malformed_event_ignored", [
    ("bad_event_" + str(index), (text, PATH, "unknown"))
    for index, text in enumerate(("", "PRIVATE_CONTACT", event(path=PATH + "1"),
        event(path="/org/bluez/obex/client/session1/transfer0"), event(kind="method_return"),
        event(interface="org.other"), event(member="Other"), event(transfer="org.other"),
        event(key="Other"), event(signature="v"), event(state="queued"), event(state="active"),
        event(state="PRIVATE_CONTACT"), event()[:event().index('STRING "complete";')],
        event().replace('STRING "complete";', 'STRING "complete'),
        event().replace("Path=", "WrongPath=")))], check)
add_cases(MonitorContracts, "N1", "invalid_transfer_path_ignored", [
    ("bad_path_" + str(index), (event(), path, "unknown"))
    for index, path in enumerate(("", PATH + "x", PATH + "/child", "PRIVATE_CONTACT", "/transfer0", PATH + "\n"))], check)


def check_arguments(self, args):
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        self.assertEqual(monitor.main(args), 2)
    self.assertEqual(output.getvalue(), "unknown\n")


add_cases(MonitorContracts, "N1", "argument_count_rejected", [
    ("zero_args", []), ("one_arg", ["PRIVATE_CONTACT"]),
    ("three_args", ["a", "b", "PRIVATE_CONTACT"])], check_arguments)
