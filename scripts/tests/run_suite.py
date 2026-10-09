#!/usr/bin/env python3
"""Run contracts once and repeat only process stability scenarios."""
import argparse
from collections import Counter
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[2]


def flatten(suite):
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            yield from flatten(test)
        else:
            yield test


def inventory(suite):
    entries = []
    for test in flatten(suite):
        method = getattr(test, test._testMethodName)
        entries.append({"id": test.id(), "category": getattr(method, "category", "Positive")})
    return entries


def process_stability(test):
    """Select actual subprocess/FIFO/signal interactions, not simulated races."""
    module = type(test).__module__
    name = type(test).__name__
    category = getattr(getattr(test, test._testMethodName), "category", "Positive")
    if (module, name) in {
        ("test_obex_contract", "ObexContracts"),
        ("test_map_send_contract", "SendContracts"),
        ("test_map_events_contract", "MapEventContracts"),
    }:
        return True
    if module in {"test_remaining_contracts", "test_packaging_branches"}:
        return category == "N9"
    return module == "test_hfp_contract_extended" and "dial_terminated" in test._testMethodName


class ProgressResult(unittest.TextTestResult):
    def startTest(self, test):
        super().startTest(test)
        if self.testsRun == 1 or self.testsRun % 100 == 0:
            self.stream.writeln(f"progress={self.testsRun} current={test.id()}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--inventory", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--trace-first", action="store_true")
    parser.add_argument("--lane", choices=("all", "process-stability"), default="all")
    args = parser.parse_args()
    if not 1 <= args.runs <= 10:
        parser.error("--runs must be 1..10")
    if args.runs > 1:
        results = []
        report = args.report.resolve() if args.report else None
        if report:
            report.parent.mkdir(parents=True, exist_ok=True)
        for index in range(1, args.runs + 1):
            started = time.monotonic()
            trace_directory = None
            lane = args.lane if index == 1 else "process-stability"
            print(f"run_started={index}/{args.runs} lane={lane}", flush=True)
            python_command = [sys.executable, str(Path(__file__).resolve()), "--lane", lane]
            if report and index == 1:
                python_command += ["--inventory", str(report.parent / "test-inventory.json")]
            if report and index == 2:
                python_command += ["--inventory", str(report.parent / "stability-inventory.json")]
            commands = [python_command]
            if lane == "all":
                commands.insert(0, ["cargo", "test", "--workspace", "--all-features"])
            for command in commands:
                environment = os.environ.copy()
                if args.trace_first and index == 1 and command == python_command:
                    trace_root = (report.parent if report else ROOT / "work") / "source-trace" / f"run-{os.getpid()}"
                    trace_root.mkdir(parents=True, exist_ok=True)
                    trace_directory = str(trace_root)
                    environment.update(
                        PYTHONPATH=str(ROOT / "scripts/tests/trace_site"),
                        NATIVEPAIR_TRACE_ROOT=str(ROOT),
                        NATIVEPAIR_PYTHON_TRACE=str(trace_root / "python"),
                        NATIVEPAIR_TEST_TRACE=str(trace_root / "bash-lines.txt"))
                result = subprocess.run(command, cwd=ROOT, env=environment, check=False)
                if result.returncode:
                    if report:
                        results.append({"run": index, "lane": lane, "status": "failed", "exit_code": result.returncode})
                        report.write_text(json.dumps(results, indent=2) + "\n")
                    return result.returncode
            duration = time.monotonic() - started
            results.append({"run": index, "lane": lane, "status": "passed", "duration_seconds": round(duration, 3)})
            if trace_directory:
                results[-1]["trace_directory"] = trace_directory
            if report:
                report.write_text(json.dumps(results, indent=2) + "\n")
            print(f"run_passed={index}/{args.runs} duration_seconds={duration:.3f}", flush=True)
        return 0
    suite = unittest.defaultTestLoader.discover(str(ROOT / "scripts/tests"))
    if args.lane == "process-stability":
        suite = unittest.TestSuite(test for test in flatten(suite) if process_stability(test))
        if suite.countTestCases() == 0:
            parser.error("process-stability lane must not be empty")
    entries = inventory(suite)
    print(f"lane={args.lane} test_count={len(entries)}", flush=True)
    print("category_counts=" + json.dumps(dict(sorted(Counter(entry["category"] for entry in entries).items()))), flush=True)
    if args.inventory:
        args.inventory.write_text(json.dumps(entries, indent=2) + "\n")
    result = unittest.TextTestRunner(verbosity=0, resultclass=ProgressResult).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
