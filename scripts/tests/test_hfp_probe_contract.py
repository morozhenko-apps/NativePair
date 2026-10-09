"""Contract tests run real HFP Bash probes against fake BlueZ/D-Bus commands.

No actual Bluetooth connection, telephone call or external network is used.
"""
from pathlib import Path
import unittest
from scenarios import category

REPO = Path(__file__).resolve().parents[2]
CALL = REPO / "scripts" / "probe-hfp-call.sh"
SCO = REPO / "scripts" / "probe-hfp-sco.sh"
RECIPIENT = "15551234567"  # synthetic fixture, never logged



class GuardedProbeTests(unittest.TestCase):
    def run_probe(self, script, scenario="normal", dial=False):
        from probe_harness import run_probe, route, assert_safe, commands
        routes = []
        config = {}
        if scenario == "preexisting":
            config["initial"] = {"call_exists": True}
        elif scenario == "ambiguous_dial":
            routes.append(route("busctl", "Dial s", exit=1))
        elif scenario == "already_active":
            config["transport_on_dial"] = "active"
        elif scenario == "pending_then_active":
            routes.append(route("busctl", "get-property.*/ag0 .*State", replies=[
                {"stdout": 's "idle"'}, {"stdout": 's "pending"'}, {"stdout": 's "active"'}]))
        elif scenario == "active_after_error":
            routes += [route("busctl", " Activate$", "org.pipewire.Telephony.Error.InvalidState", exit=1),
                       route("busctl", "get-property.*/ag0 .*State", replies=[
                           {"stdout": 's "idle"'}, {"stdout": 's "idle"'}, {"stdout": 's "active"'}])]
        elif scenario == "not_active":
            config["active_calls"] = 'a(oa{sv}) 1 "/org/pipewire/Telephony/ag0/call0" 1 "State" s "dialing"'
        if script == SCO and scenario in ("normal", "not_active"):
            routes.append(route("busctl", " Activate$", "org.pipewire.Telephony.Error.InvalidState", exit=1))
        result = run_probe(script.name, args=("--dial",) if dial else (), routes=routes, config=config)
        for private in (RECIPIENT, "PRIVATE_CONTACT"):
            self.assertNotIn(private, result.stdout + result.stderr)
        self.assertEqual(result.remaining, [])
        state = {**result.state, "dial_attempts": len(commands(result, "Dial")),
                 "hangup_attempts": len(commands(result, "HangupAll")),
                 "activate_attempts": len(commands(result, "Activate"))}
        return result, state

    @category("Positive")
    def test_given_call_preflight_when_probe_runs_then_no_call_mutation(self):
        run, state = self.run_probe(CALL)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn("probe_complete=preflight", run.stdout)
        self.assertEqual(state["dial_attempts"], 0)
        self.assertEqual(state["hangup_attempts"], 0)

    @category("Positive")
    def test_given_sco_preflight_when_probe_runs_then_no_call_or_transport_mutation(self):
        run, state = self.run_probe(SCO)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn("probe_complete=preflight", run.stdout)
        self.assertEqual(state["dial_attempts"], 0)
        self.assertEqual(state["hangup_attempts"], 0)
        self.assertEqual(state["activate_attempts"], 0)

    @category("Positive")
    def test_given_owned_call_when_probe_succeeds_then_dial_and_hangup_once(self):
        run, state = self.run_probe(CALL, dial=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn("probe_complete=yes", run.stdout)
        self.assertEqual(state["dial_attempts"], 1)
        self.assertEqual(state["hangup_attempts"], 1)
        self.assertFalse(state["call_exists"])
        self.assertNotIn("cleanup_hangup_attempted=yes", run.stdout)

    @category("N3")
    def test_given_ambiguous_call_dial_reply_when_probe_fails_then_owned_call_cleaned_up(self):
        run, state = self.run_probe(CALL, "ambiguous_dial", dial=True)
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("dial_call_accepted=no", run.stdout)
        self.assertIn("cleanup_hangup_attempted=yes", run.stdout)
        self.assertIn("cleanup_hangup_accepted=yes", run.stdout)
        self.assertEqual(state["hangup_attempts"], 1)
        self.assertFalse(state["call_exists"])

    @category("N3")
    def test_given_ambiguous_sco_dial_reply_when_probe_fails_then_owned_call_cleaned_up(self):
        run, state = self.run_probe(SCO, "ambiguous_dial", dial=True)
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("sco_error=dial_failed", run.stdout)
        self.assertIn("cleanup_hangup_attempted=yes", run.stdout)
        self.assertEqual(state["hangup_attempts"], 1)
        self.assertFalse(state["call_exists"])

    @category("N7")
    def test_given_existing_call_when_dial_requested_then_existing_call_untouched(self):
        for script in (CALL, SCO):
            with self.subTest(script=script.name):
                run, state = self.run_probe(script, "preexisting", dial=True)
                self.assertNotEqual(run.returncode, 0)
                self.assertIn("preexisting_call_present=yes", run.stdout)
                self.assertEqual(state["dial_attempts"], 0)
                self.assertEqual(state["hangup_attempts"], 0)
                self.assertTrue(state["call_exists"])

    @category("N3")
    def test_given_sco_activate_failure_when_probe_fails_then_owned_call_cleaned_up(self):
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

    @category("N5")
    def test_given_auto_active_transport_when_sco_observed_then_activate_skipped(self):
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

    @category("N5")
    def test_given_pending_transport_when_sco_observed_then_auto_activation_awaited(self):
        run, state = self.run_probe(SCO, "pending_then_active", dial=True)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("transport_state_before_activate=pending", run.stdout)
        self.assertIn("transport_pending_wait=yes", run.stdout)
        self.assertIn("transport_activate_invoked=no", run.stdout)
        self.assertIn("transport_activation_path=pending_wait", run.stdout)
        self.assertEqual(state["activate_attempts"], 0)
        self.assertEqual(state["hangup_attempts"], 1)

    @category("N5")
    def test_given_activate_error_and_active_transport_when_sco_observed_then_success(self):
        run, state = self.run_probe(SCO, "active_after_error", dial=True)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("transport_activate_accepted=no", run.stdout)
        self.assertIn("transport_state_after_activate_error=active", run.stdout)
        self.assertIn("transport_activation_path=error_but_transport_active", run.stdout)
        self.assertIn("probe_complete=yes", run.stdout)
        self.assertEqual(state["activate_attempts"], 1)
        self.assertEqual(state["hangup_attempts"], 1)

    @category("Positive")
    def test_given_idle_transport_when_activate_succeeds_then_sco_active(self):
        run, state = self.run_probe(SCO, "activate_success", dial=True)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("transport_activate_accepted=yes", run.stdout)
        self.assertIn("transport_state_after_activate=active", run.stdout)
        self.assertIn("transport_activation_path=accepted", run.stdout)
        self.assertIn("probe_complete=yes", run.stdout)
        self.assertEqual(state["activate_attempts"], 1)
        self.assertEqual(state["hangup_attempts"], 1)

    @category("N2")
    def test_given_call_wait_timeout_when_sco_fails_then_cleanup_without_activate(self):
        run, state = self.run_probe(SCO, "not_active", dial=True)
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("sco_error=call_not_active", run.stdout)
        self.assertEqual(state["activate_attempts"], 0)
        self.assertEqual(state["hangup_attempts"], 1)
        self.assertFalse(state["call_exists"])


if __name__ == "__main__":
    unittest.main()
