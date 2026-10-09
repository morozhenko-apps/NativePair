"""Execute actual built Rust entry points; no replacement of argument logic."""
import os
from pathlib import Path
import subprocess
import unittest

from scenarios import add_cases
from probe_harness import REPO


class BinaryContracts(unittest.TestCase):
    pass


def check(self, value):
    name, args, code, stdout, stderr = value
    binary = Path(os.environ.get("NATIVEPAIR_TEST_BIN_DIR", str(REPO / "target/debug"))) / name
    if not binary.is_file():
        self.fail("Build binaries before tests: cargo build --workspace --locked")
    result = subprocess.run([str(binary), *args], capture_output=True, text=True,
                            timeout=5, check=False)
    self.assertEqual(result.returncode, code)
    self.assertEqual(result.stdout, stdout)
    self.assertEqual(result.stderr, stderr)


cases = []
for binary, description in (("nativepair", "NativePair"), ("nativepair-daemon", "NativePair daemon")):
    version = "0.1.0"
    help_ = (f"NativePair {version}\n\nUsage:\n  nativepair [--help]\n  nativepair --version\n\n"
             "The protocol-facing CLI will be added after M1 feasibility results are recorded.\n")
    error = ("Unsupported arguments. Run 'nativepair --help'.\n" if binary == "nativepair" else
             "Unsupported arguments. Use --version or start without arguments.\n")
    default = ("NativePair CLI foundation: contacts=Unknown\n" if binary == "nativepair" else
               "NativePair daemon foundation: messages=Unknown\n")
    cases.append((binary + "_default", (binary, (), 0, default, "")))
    for flag in ("--version", "-V"):
        cases.append((binary + "_version_" + flag.replace("-", ""), (binary, (flag,), 0, description + " " + version + "\n", "")))
    if binary == "nativepair":
        for flag in ("--help", "-h"):
            cases.append((binary + "_help_" + flag.replace("-", ""), (binary, (flag,), 0, help_, "")))
    for index, args in enumerate((('--unknown',), ('PRIVATE_CONTACT',), ('--version', 'extra'), ('-V', 'extra'),
                                  ('--help', 'extra'), ('-h', 'extra'), ('',), ('--version', '--version'))):
        cases.append((binary + "_bad_" + str(index), (binary, args, 2, "", error)))
    if binary == "nativepair-daemon":
        for flag in ("--help", "-h"):
            cases.append((binary + "_help_rejected_" + flag.replace("-", ""), (binary, (flag,), 2, "", error)))
add_cases(BinaryContracts, "Positive", "binary_invoked", [item for item in cases if item[1][2] == 0], check)
add_cases(BinaryContracts, "N1", "invalid_arguments_rejected", [item for item in cases if item[1][2] != 0], check)
