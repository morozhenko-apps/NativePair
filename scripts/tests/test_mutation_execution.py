"""Mutation execution must see same-length edits without timestamp sleeps."""

import os
from pathlib import Path
import tempfile
import unittest

import review_mutations
from scenarios import category


class MutationExecutionContracts(unittest.TestCase):
    @category("N6")
    def test_given_same_size_same_mtime_edit_when_executed_then_assertion_kills_mutation(self):
        # Arrange
        with tempfile.TemporaryDirectory(prefix="nativepair-bytecode-contract-") as directory:
            root = Path(directory)
            tests = root / "scripts/tests"
            tests.mkdir(parents=True)
            subject = tests / "subject.py"
            subject.write_text("VALUE = 1\n")
            (tests / "test_fixture.py").write_text(
                "import unittest\nimport subject\n"
                "class Fixture(unittest.TestCase):\n"
                "    def test_contract(self):\n"
                "        self.assertEqual(subject.VALUE, 1)\n")
            stamp = subject.stat()
            # Act
            baseline = review_mutations.execute(root, "test_fixture.py", "")
            subject.write_text("VALUE = 2\n")
            os.utime(subject, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
            mutated = review_mutations.execute(root, "test_fixture.py", "")
            # Assert
            self.assertEqual(subject.stat().st_size, stamp.st_size)
            self.assertEqual(subject.stat().st_mtime_ns, stamp.st_mtime_ns)
            self.assertEqual(baseline.returncode, 0, baseline.stderr)
            self.assertNotEqual(mutated.returncode, 0)
            self.assertIn("FAIL: test_contract", mutated.stderr)
            self.assertIn("AssertionError: 2 != 1", mutated.stderr)
            self.assertEqual(list(root.rglob("*.pyc")), [])
