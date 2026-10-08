"""Contract tests run real HFP Bash probes against fake BlueZ/D-Bus commands.

No actual Bluetooth connection, telephone call or external network is used.
"""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[2]
CALL = REPO / "scripts" / "probe-hfp-call.sh"
SCO = REPO / "scripts" / "probe-hfp-sco.sh"
RECIPIENT = "15551234567"  # synthetic fixture, never logged

FAKE_BLUEZ = r'''#!/usr/bin/env python3
import sys
if sys.argv[1] == "info":
    print("  Paired: yes")
    print("  UUID: Handsfree Audio Gateway (0000111f-0000-1000-8000-00805f9b34fb)")
elif sys.argv[1] == "connect":
    print("Connection successful")
else:
    sys.exit(1)
'''

FAKE_BUSCTL = r'''#!/usr/bin/env python3
import json
import os
import sys

path = os.environ["NATIVEPAIR_TEST_STATE"]
with open(path, encoding="utf-8") as file:
    state = json.load(file)

args = sys.argv[1:]
if args and args[0] == "--user":
    args = args[1:]
if not args:
    sys.exit(2)

command = args[0]
method = args[4] if len(args) > 4 else ""
rc = 0

if command == "introspect":
    print("org.pipewire.Telephony.AudioGatewayTransport1 Activate")
    print("org.pipewire.Telephony.AudioGateway1 Dial HangupAll")
elif command == "get-property":
    prop = args[4]
    if prop == "RejectSCO":
        print("b false")
    elif prop == "State":
        if "/call" in args[2]:
            print('s "' + state["call_state"] + '"')
        else:
            state["transport_reads"] += 1
            if (state["scenario"] == "pending_then_active"
                    and state["transport_reads"] >= 3):
                state["transport_state"] = "active"
            print('s "' + state["transport_state"] + '"')
    else:
        rc = 2
elif command == "call":
    if method == "GetModems":
        print('a(oa{sv}) 1 "/org/pipewire/Telephony/ag0" 0')
    elif method == "GetCalls":
        if state["call_exists"]:
            print('a(oa{sv}) 1 "/org/pipewire/Telephony/ag0/call0" 1 "State" s "' +
                  state["call_state"] + '"')
        else:
            print("a(oa{sv}) 0")
    elif method == "Dial":
        state["dial_attempts"] += 1
        state["call_exists"] = True  # Simulate side-effect preceding D-Bus reply
        if state["scenario"] == "ambiguous_dial":
            rc = 1
        elif state["scenario"] == "already_active":
            state["transport_state"] = "active"
        elif state["scenario"] == "pending_then_active":
            state["transport_state"] = "pending"
    elif method == "HangupAll":
        state["hangup_attempts"] += 1
        state["call_exists"] = False
    elif method == "Activate":
        state["activate_attempts"] += 1
        if state["scenario"] == "activate_success":
            state["transport_state"] = "active"
        elif state["scenario"] == "active_after_error":
            state["transport_state"] = "active"
            print("org.pipewire.Telephony.Error.InvalidState")
            rc = 1
        else:
            print("org.pipewire.Telephony.Error.InvalidState")
            rc = 1
    else:
        rc = 2
else:
    rc = 2

with open(path, "w", encoding="utf-8") as file:
    json.dump(state, file)
sys.exit(rc)
'''


class GuardedProbeTests(unittest.TestCase):
    def run_probe(self, script, scenario="normal", dial=False):
        with tempfile.TemporaryDirectory(prefix="nativepair-hfp-test-") as td:
            directory = Path(td)
            bin_dir = directory / "bin"
            bin_dir.mkdir()
            for executable, content in (
                ("bluetoothctl", FAKE_BLUEZ),
                ("busctl", FAKE_BUSCTL),
                ("pw-dump", "#!/bin/sh\nprintf '%s\\n' '[{\"type\":\"PipeWire:Interface:Node\",\"info\":{\"props\":{\"api.bluez5.address\":\"02:00:00:00:00:01\",\"api.bluez5.profile\":\"headset-head-unit\",\"media.class\":\"Audio/Source\"}}},{\"type\":\"PipeWire:Interface:Node\",\"info\":{\"props\":{\"api.bluez5.address\":\"02:00:00:00:00:01\",\"api.bluez5.profile\":\"headset-head-unit\",\"media.class\":\"Audio/Sink\"}}}]'\n"),
                ("wpctl", "#!/bin/sh\nexit 0\n"),
            ):
                path = bin_dir / executable
                path.write_text(content, encoding="utf-8")
                path.chmod(0o755)
            state_file = directory / "state.json"
            state = {
                "scenario": scenario,
                "call_exists": scenario == "preexisting",
                "call_state": "dialing" if scenario == "not_active" else "active",
                "dial_attempts": 0,
                "hangup_attempts": 0,
                "activate_attempts": 0,
                "transport_state": "idle",
                "transport_reads": 0,
            }
            state_file.write_text(json.dumps(state), encoding="utf-8")
            env = {
                **os.environ,
                "PATH": str(bin_dir) + os.pathsep + os.environ["PATH"],
                "NATIVEPAIR_TEST_STATE": str(state_file),
                "NATIVEPAIR_DEVICE": "02:00:00:00:00:01",
                "NATIVEPAIR_CALL_RECIPIENT": RECIPIENT,
                "NATIVEPAIR_SCO_STATE_TIMEOUT": "1",
                "NATIVEPAIR_CALL_ACTIVE_TIMEOUT": "1",
                "NATIVEPAIR_HFP_CONNECT_TIMEOUT": "1",
                "NATIVEPAIR_SCO_HUMAN_WINDOW": "1",
            }
            argv = ["bash", str(script)]
            if dial:
                argv.append("--dial")
            process = subprocess.run(
                argv, env=env, text=True, capture_output=True,
                timeout=15, check=False,
            )
            state_after = json.loads(state_file.read_text(encoding="utf-8"))
            self.assertNotIn(RECIPIENT, process.stdout)
            self.assertNotIn(RECIPIENT, process.stderr)
            return process, state_after

    def test_call_preflight_never_mutates_call(self):
        run, state = self.run_probe(CALL)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn("probe_complete=preflight", run.stdout)
        self.assertEqual(state["dial_attempts"], 0)
        self.assertEqual(state["hangup_attempts"], 0)

    def test_sco_preflight_never_mutates_call_or_transport(self):
        run, state = self.run_probe(SCO)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn("probe_complete=preflight", run.stdout)
        self.assertEqual(state["dial_attempts"], 0)
        self.assertEqual(state["hangup_attempts"], 0)
        self.assertEqual(state["activate_attempts"], 0)

    def test_call_probe_success_dials_and_hangs_up_once(self):
        run, state = self.run_probe(CALL, dial=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn("probe_complete=yes", run.stdout)
        self.assertEqual(state["dial_attempts"], 1)
        self.assertEqual(state["hangup_attempts"], 1)
        self.assertFalse(state["call_exists"])
        self.assertNotIn("cleanup_hangup_attempted=yes", run.stdout)

    def test_call_probe_ambiguous_dial_reply_triggers_cleanup(self):
        run, state = self.run_probe(CALL, "ambiguous_dial", dial=True)
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("dial_call_accepted=no", run.stdout)
        self.assertIn("cleanup_hangup_attempted=yes", run.stdout)
        self.assertIn("cleanup_hangup_accepted=yes", run.stdout)
        self.assertEqual(state["hangup_attempts"], 1)
        self.assertFalse(state["call_exists"])

    def test_sco_probe_ambiguous_dial_reply_triggers_cleanup(self):
        run, state = self.run_probe(SCO, "ambiguous_dial", dial=True)
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("sco_error=dial_failed", run.stdout)
        self.assertIn("cleanup_hangup_attempted=yes", run.stdout)
        self.assertEqual(state["hangup_attempts"], 1)
        self.assertFalse(state["call_exists"])

    def test_existing_call_is_never_hung_up(self):
        for script in (CALL, SCO):
            with self.subTest(script=script.name):
                run, state = self.run_probe(script, "preexisting", dial=True)
                self.assertNotEqual(run.returncode, 0)
                self.assertIn("preexisting_call_present=yes", run.stdout)
                self.assertEqual(state["dial_attempts"], 0)
                self.assertEqual(state["hangup_attempts"], 0)
                self.assertTrue(state["call_exists"])

    def test_sco_activate_failure_triggers_cleanup(self):
        run, state = self.run_probe(SCO, dial=True)
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("call_active_observed=yes", run.stdout)
        self.assertIn("sco_error=activate_failed_transport_inactive", run.stdout)
        self.assertIn("transport_state_after_activate_error=idle", run.stdout)
        self.assertIn("activate_error_class=org.pipewire.Telephony.Error.InvalidState", run.stdout)
        self.assertIn("cleanup_hangup_attempted=yes", run.stdout)
        self.assertEqual(state["dial_attempts"], 1)
        self.assertEqual(state["activate_attempts"], 1)
        self.assertEqual(state["hangup_attempts"], 1)
        self.assertFalse(state["call_exists"])

    def test_sco_auto_active_skips_activate(self):
        run, state = self.run_probe(SCO, "already_active", dial=True)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("transport_state_before_activate=active", run.stdout)
        self.assertIn("transport_already_active_before_activate=yes", run.stdout)
        self.assertIn("transport_activate_invoked=no", run.stdout)
        self.assertIn("transport_activation_path=already_active", run.stdout)
        self.assertIn("pipewire_hfp_nodes_observed=yes", run.stdout)
        self.assertEqual(state["activate_attempts"], 0)
        self.assertEqual(state["hangup_attempts"], 1)
        self.assertFalse(state["call_exists"])

    def test_sco_pending_transport_waits_for_auto_activation(self):
        run, state = self.run_probe(SCO, "pending_then_active", dial=True)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("transport_state_before_activate=pending", run.stdout)
        self.assertIn("transport_pending_wait=yes", run.stdout)
        self.assertIn("transport_activate_invoked=no", run.stdout)
        self.assertIn("transport_activation_path=pending_wait", run.stdout)
        self.assertEqual(state["activate_attempts"], 0)
        self.assertEqual(state["hangup_attempts"], 1)

    def test_sco_error_but_transport_auto_active(self):
        run, state = self.run_probe(SCO, "active_after_error", dial=True)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("transport_activate_accepted=no", run.stdout)
        self.assertIn("transport_state_after_activate_error=active", run.stdout)
        self.assertIn("transport_activation_path=error_but_transport_active", run.stdout)
        self.assertIn("probe_complete=yes", run.stdout)
        self.assertEqual(state["activate_attempts"], 1)
        self.assertEqual(state["hangup_attempts"], 1)

    def test_sco_explicit_activate_success(self):
        run, state = self.run_probe(SCO, "activate_success", dial=True)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("transport_activate_accepted=yes", run.stdout)
        self.assertIn("transport_state_after_activate=active", run.stdout)
        self.assertIn("transport_activation_path=accepted", run.stdout)
        self.assertIn("probe_complete=yes", run.stdout)
        self.assertEqual(state["activate_attempts"], 1)
        self.assertEqual(state["hangup_attempts"], 1)

    def test_sco_wait_timeout_triggers_cleanup_without_activate(self):
        run, state = self.run_probe(SCO, "not_active", dial=True)
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("sco_error=call_not_active", run.stdout)
        self.assertEqual(state["activate_attempts"], 0)
        self.assertEqual(state["hangup_attempts"], 1)
        self.assertFalse(state["call_exists"])


if __name__ == "__main__":
    unittest.main()
