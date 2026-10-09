#!/usr/bin/env python3
"""Reproduce assertion-level mutation trials in disposable repository copies."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]

# Each mutation has one explicit invariant and runs the same tests before/after.
TRIALS = [
    ("capability_available_inverted", "crates/nativepair-core/src/lib.rs",
     "self.availability(capability) == Availability::Available",
     "self.availability(capability) != Availability::Available", "rust", ""),
    ("transition_previous_value_discarded", "crates/nativepair-core/src/lib.rs",
     ".insert(capability, availability)\n            .unwrap_or(Availability::Unknown)",
     ".insert(capability, availability);\n        Availability::Unknown", "rust", ""),
    ("unrelated_transfer_accepted", "scripts/probe_obex_monitor.py",
     'if not re.search(r"\\bPath=" + re.escape(path) + r"(?=\\s|$)", block):',
     'if False:', "test_obex_monitor.py", "bad_event_2"),
    ("unrelated_event_interface_accepted", "scripts/probe_obex_monitor.py",
     'if not re.search(r"\\bInterface=org\\.freedesktop\\.DBus\\.ObjectManager(?=\\s|$)", block):',
     'if False:', "test_map_events_contract.py", "wrong_dbus_interface"),
    ("duplicate_sms_send", "scripts/probe-map-send.sh",
     '"$BMSG_FILE" outbox 3   Transparent b true   Retry b false   Charset s utf8 >"$PUSH_REPLY" 2>&1',
     '"$BMSG_FILE" outbox 3   Transparent b true   Retry b false   Charset s utf8 >"$PUSH_REPLY" 2>&1\nbusctl --user call org.bluez.obex "$SESSION_PATH" org.bluez.obex.MessageAccess1 PushMessage ssa{sv} "$BMSG_FILE" outbox 0 >/dev/null 2>&1',
     "test_map_send_contract.py", ""),
    ("sms_retry_enabled", "scripts/probe-map-send.sh", "Retry b false", "Retry b true",
     "test_map_send_contract.py", ""),
    ("ambiguous_dial_cleanup_removed", "scripts/probe-hfp-call.sh",
     'if [[ "$DIAL_ATTEMPTED" == yes && "$HANGUP_DONE" != yes && -n "$AG_PATH" ]]; then',
     'if false; then', "test_hfp_contract_extended.py", "ambiguous_dial"),
    ("pending_transport_activated_twice", "scripts/probe-hfp-sco.sh",
     'ACTIVATE_RESULT=pending_wait',
     'ACTIVATE_RESULT=pending_wait\n    busctl --user call "$TELEPHONY_SERVICE" "$AG_PATH" "$TRANSPORT_IFACE" Activate >/dev/null 2>&1',
     "test_hfp_contract_extended.py", "pending"),
    ("single_endpoint_proves_duplex", "scripts/probe-hfp-sco.sh",
     "count >= 2 and source and sink", "count >= 1 and (source or sink)",
     "test_hfp_contract_extended.py", "nodes"),
    ("zero_error_growth_counted", "scripts/probe-audio-health.sh",
     "if max_err.get(nid, 0) - first_err.get(nid, 0) > 0",
     "if max_err.get(nid, 0) - first_err.get(nid, 0) >= 0",
     "test_audio_diagnostics_contract.py", ""),
    ("timer_maximum_rejected", "scripts/probe-obex-read.sh",
     'CONNECT_TIMEOUT > 922337203685477580',
     'CONNECT_TIMEOUT >= 922337203685477580',
     "test_remaining_contracts.py", "probe_obex_read_shNATIVEPAIR_OBEX_TIMEOUT922337203685477580"),
    ("wrong_archive_sidecar_accepted", "scripts/verify-deb.sh",
     '($2 == name || $2 == "*" name)', '1',
     "test_packaging_contract.py", "wrong_target"),
    ("runtime_dependency_not_checked", "scripts/verify-deb.sh",
     'if ! dependency_present "$dependency"; then', 'if false; then',
     "test_packaging_contract.py", "invalid_metadata"),
    ("duplicate_node_ids_accepted", "scripts/probe_audio_graph.py",
     'return list(nodes.values())', 'return list(nodes.values()) * 2',
     "test_audio_graph.py", "duplicate_ids"),
    ("private_argument_printed", "scripts/probe-obex-session.sh",
     'echo "Unknown argument." >&2', 'echo "Unknown argument: $1" >&2',
     "test_probe_parameters.py", "probe_obex_session_sh_when_private_argument"),
    ("codec_mapping_changed", "scripts/probe-hfp-audio.sh",
     '1) echo "transport_codec=cvsd"', '1) echo "transport_codec=msbc"',
     "test_hfp_contract_extended.py", "codec_1"),
    ("temporary_artifacts_not_removed", "scripts/probe-obex-session.sh",
     'rm -rf "$TMP_DIR"', ':',
     "test_remaining_contracts.py", "interrupt_probe_obex_session"),
    ("duplicate_owned_call_dial", "scripts/probe-hfp-call.sh",
     'org.pipewire.Telephony.AudioGateway1 Dial s "$RECIPIENT" >"$DIAL_REPLY" 2>&1',
     'org.pipewire.Telephony.AudioGateway1 Dial s "$RECIPIENT" >"$DIAL_REPLY" 2>&1\nbusctl --user call "$TELEPHONY_SERVICE" "$AG_PATH" org.pipewire.Telephony.AudioGateway1 Dial s "$RECIPIENT" >/dev/null 2>&1',
     "test_hfp_probe_contract.py", "owned_call_when_probe_succeeds"),
    ("preflight_no_dial_guard_removed", "scripts/probe-hfp-call.sh",
     'if [[ "$DO_DIAL" != yes ]]; then', 'if false; then',
     "test_hfp_probe_contract.py", "call_preflight"),
    ("zero_prefixed_array_count_accepted", "scripts/probe-obex-read.sh",
     '$2 ~ /^(0|[1-9][0-9]*)$/ && length($2) <= 10',
     '$2 ~ /^[0-9]+$/ && length($2) <= 10',
     "test_obex_contract.py", "leading_zero"),
    ("zero_prefixed_phonebook_size_accepted", "scripts/probe-obex-read.sh",
     '$2 ~ /^(0|[1-9][0-9]*)$/ && length($2) <= 5',
     '$2 ~ /^[0-9]+$/ && length($2) <= 5',
     "test_obex_contract.py", "leading_zero"),
    ("sdp_interrupt_ignored", "scripts/probe-map-sdp.sh",
     "trap 'exit 130' INT", ":", "test_remaining_contracts.py", "int_defaults"),
    ("mns_interrupt_ignored", "scripts/probe-mns.sh",
     "trap 'exit 130' INT", ":", "test_remaining_contracts.py", "int_defaults"),
    ("build_interrupt_ignored", "scripts/build-deb.sh",
     "trap 'exit 130' INT", ":", "test_packaging_branches.py", "interrupted_before_build"),
    ("verify_interrupt_ignored", "scripts/verify-deb.sh",
     "trap 'exit 130' INT", ":", "test_packaging_branches.py", "interrupted_during_verify"),
]


def execute(root, pattern, selected):
    if pattern == "rust":
        command = ["cargo", "test", "--workspace", "--all-features", "--offline"]
    else:
        command = [sys.executable, "-m", "unittest", "discover", "-s", "scripts/tests", "-p", pattern, "-v"]
        if selected:
            command += ["-k", selected]
    return subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=180, check=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--start-at", choices=[trial[0] for trial in TRIALS])
    args = parser.parse_args()
    start = next((index for index, trial in enumerate(TRIALS) if trial[0] == args.start_at), 0)
    preceding = {trial[0] for trial in TRIALS[:start]}
    results = ([item for item in json.loads(args.output.read_text()) if item["mutation"] in preceding]
               if start and args.output.exists() else [])
    with tempfile.TemporaryDirectory(prefix="nativepair-mutation-") as directory:
        root = Path(directory)
        for name in ("scripts", "crates", "packaging"):
            shutil.copytree(ROOT / name, root / name, ignore=shutil.ignore_patterns("__pycache__"))
        for name in ("Cargo.toml", "Cargo.lock", "rust-toolchain.toml", "LICENSE", "NOTICE", "README.md"):
            shutil.copy(ROOT / name, root / name)
        for name, file, before, after, pattern, selected in TRIALS[start:]:
            path = root / file
            original = path.read_text()
            if original.count(before) != 1:
                raise RuntimeError(f"Mutation anchor is not unique: {name}")
            baseline = execute(root, pattern, selected)
            if baseline.returncode or (pattern != "rust" and "Ran 0 tests" in baseline.stderr):
                raise RuntimeError(f"Mutation baseline failed: {name}\n{baseline.stdout}{baseline.stderr}")
            path.write_text(original.replace(before, after))
            try:
                mutated = execute(root, pattern, selected)
            finally:
                path.write_text(original)
            output = mutated.stdout + mutated.stderr
            killed = (mutated.returncode != 0 and
                      ("FAIL:" in output or (pattern == "rust" and "test result: FAILED" in output)))
            results.append({"mutation": name, "file": file, "pattern": pattern,
                            "selector": selected, "baseline": "passed",
                            "result": "killed" if killed else "survived_or_invalid",
                            "evidence": output})
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(results, indent=2) + "\n")
            print(f"mutation={name} result={results[-1]['result']}", flush=True)
    return 0 if all(item["result"] == "killed" for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
