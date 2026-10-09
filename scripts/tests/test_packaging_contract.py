"""Actual Debian archive/checksum contracts and isolated native build staging."""
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from scenarios import add_cases, category
from probe_harness import REPO


def run(argv, env=None, cwd=None):
    return subprocess.run(argv, cwd=cwd, env=env, text=True, capture_output=True,
                          timeout=20, check=False)


def archive(root, fields=None, omitted=(), nonexecutables=(), failures=()):
    content = root / "package"
    (content / "DEBIAN").mkdir(parents=True)
    metadata = {"Package": "nativepair", "Version": "0.1.0", "Architecture": "amd64",
                "Maintainer": "Synthetic Test <test@example.invalid>",
                "Depends": "bluez, bluez-obexd", "Description": "Synthetic package"}
    metadata.update(fields or {})
    (content / "DEBIAN/control").write_text("".join(f"{key}: {value}\n" for key, value in metadata.items()))
    for path in ("usr/bin/nativepair", "usr/libexec/nativepair-daemon",
                 "usr/share/doc/nativepair/LICENSE", "usr/share/doc/nativepair/NOTICE",
                 "usr/share/doc/nativepair/README.md"):
        if path in omitted:
            continue
        target = content / path
        target.parent.mkdir(parents=True, exist_ok=True)
        if path in ("usr/bin/nativepair", "usr/libexec/nativepair-daemon"):
            target.write_text("#!/bin/sh\n" + ("exit 1\n" if path in failures else "printf 'NativePair synthetic 0.1.0\\n'\n"))
            target.chmod(0o644 if path in nonexecutables else 0o755)
        else:
            target.write_text("Synthetic test fixture\n")
    package = root / "nativepair_0.1.0_amd64.deb"
    built = run(["dpkg-deb", "--root-owner-group", "--build", str(content), str(package)])
    if built.returncode:
        raise AssertionError(built.stderr)
    checksum(package)
    return package


def checksum(package, target=None):
    digest = hashlib.sha256(package.read_bytes()).hexdigest()
    package.with_suffix(package.suffix + ".sha256").write_text(f"{digest}  {target or package.name}\n")


class VerifyContracts(unittest.TestCase):
    @category("N1")
    def test_given_no_package_when_verifier_invoked_then_usage_error(self):
        result = run(["bash", str(REPO / "scripts/verify-deb.sh")])
        self.assertEqual(result.returncode, 2)

    @category("N1")
    def test_given_extra_package_when_verifier_invoked_then_usage_error(self):
        result = run(["bash", str(REPO / "scripts/verify-deb.sh"), "a", "b"])
        self.assertEqual(result.returncode, 2)

    @category("N12")
    def test_given_missing_package_when_verifier_invoked_then_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run(["bash", str(REPO / "scripts/verify-deb.sh"), str(Path(directory) / "missing.deb")])
        self.assertEqual(result.returncode, 1)


def verify(self, value):
    fields, omitted, nonexec, failures, mutation, expected = value
    with tempfile.TemporaryDirectory(prefix="nativepair-package-test-") as directory:
        root = Path(directory)
        package = archive(root, fields, omitted, nonexec, failures)
        sidecar = package.with_suffix(".deb.sha256")
        if mutation == "missing":
            sidecar.unlink()
        elif mutation == "corrupt":
            package.write_bytes(package.read_bytes() + b"corruption")
        elif mutation == "wrong_target":
            other = root / "other.deb"
            other.write_bytes(package.read_bytes())
            checksum(package, other.name)
        elif mutation == "extra_line":
            sidecar.write_text(sidecar.read_text() * 2)
        elif mutation == "invalid_checksum":
            sidecar.write_text("not-a-hash\n")
        elif mutation == "corrupt_archive":
            package.write_bytes(b"not a Debian archive")
            checksum(package)
        result = run(["bash", str(REPO / "scripts/verify-deb.sh"), str(package)])
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        if expected == 0:
            self.assertIn("Debian package verification passed:", result.stdout)


add_cases(VerifyContracts, "Positive", "valid_package_verified", [
    ("amd64", ({}, (), (), (), None, 0)),
    ("arm64_metadata", ({"Architecture": "arm64"}, (), (), (), None, 0)),
    ("version_suffix", ({"Version": "1.2.3-rc1"}, (), (), (), None, 0)),
    ("versioned_dependencies", ({"Depends": "bluez (>= 5.0), bluez-obexd (>= 5.0)"}, (), (), (), None, 0)),
], verify)
add_cases(VerifyContracts, "N6", "invalid_metadata_rejected", [
    ("field_" + str(index), (fields, (), (), (), None, 1))
    for index, fields in enumerate(({"Package": "other"}, {"Version": "1"}, {"Version": "1.2"},
        {"Architecture": "i386"}, {"Depends": "bluez"}, {"Depends": "bluez-obexd"},
        {"Depends": "bluez-extra, bluez-obexd-extra"}, {"Depends": "bluez-extra, bluez-obexd"},
        {"Depends": "bluez, bluez-obexd-extra"}))], verify)
add_cases(VerifyContracts, "N12", "missing_package_payload_rejected", [
    ("missing_" + str(index), ({}, (path,), (), (), None, 1))
    for index, path in enumerate(("usr/bin/nativepair", "usr/libexec/nativepair-daemon",
        "usr/share/doc/nativepair/LICENSE", "usr/share/doc/nativepair/NOTICE", "usr/share/doc/nativepair/README.md"))], verify)
add_cases(VerifyContracts, "N7", "nonexecutable_binary_rejected", [
    ("not_executable_" + str(index), ({}, (), (path,), (), None, 1))
    for index, path in enumerate(("usr/bin/nativepair", "usr/libexec/nativepair-daemon"))], verify)
add_cases(VerifyContracts, "N3", "failed_binary_rejected", [
    ("binary_failure_" + str(index), ({}, (), (), (path,), None, 1))
    for index, path in enumerate(("usr/bin/nativepair", "usr/libexec/nativepair-daemon"))], verify)
add_cases(VerifyContracts, "N6", "invalid_archive_or_checksum_rejected", [
    (mutation, ({}, (), (), (), mutation, 2 if mutation == "corrupt_archive" else 1))
    for mutation in ("missing", "corrupt", "wrong_target", "extra_line", "invalid_checksum", "corrupt_archive")], verify)


def build_tree(root):
    (root / "scripts").mkdir()
    (root / "packaging/debian").mkdir(parents=True)
    (root / "target/release").mkdir(parents=True)
    (root / "bin").mkdir()
    shutil.copy(REPO / "scripts/build-deb.sh", root / "scripts")
    shutil.copy(REPO / "packaging/debian/control.in", root / "packaging/debian")
    for name in ("LICENSE", "NOTICE", "README.md"):
        (root / name).write_text("Synthetic test fixture\n")
    for name in ("nativepair", "nativepair-daemon"):
        (root / "target/release" / name).write_text("#!/bin/sh\nprintf 'NativePair synthetic 0.1.0\\n'\n")
    cargo = root / "bin/cargo"
    cargo.write_text('''#!/bin/sh
if [ "$1" = metadata ]; then
  printf '%s\\n' '{"packages":[{"name":"nativepair-core","version":"0.1.0"}]}'
elif [ "$1" = build ]; then
  exit "${SYNTHETIC_BUILD_STATUS:-0}"
else
  exit 90
fi
''')
    cargo.chmod(0o755)
    environment = {"PATH": str(root / "bin") + os.pathsep + os.environ["PATH"],
                   "HOME": str(root), "LC_ALL": "C", "SOURCE_DATE_EPOCH": "1"}
    return environment


class BuildContracts(unittest.TestCase):
    pass


def build(self, value):
    env, missing, expected = value
    with tempfile.TemporaryDirectory(prefix="nativepair-build-test-") as directory:
        root = Path(directory)
        environment = build_tree(root)
        environment.update(env)
        for path in missing:
            (root / path).unlink()
        result = run(["bash", str(root / "scripts/build-deb.sh")], env=environment)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        if expected == 0:
            package = Path(result.stdout.strip().splitlines()[-1])
            self.assertTrue(package.is_file())
            validated = run(["bash", str(REPO / "scripts/verify-deb.sh"), str(package)])
            self.assertEqual(validated.returncode, 0, validated.stdout + validated.stderr)
            self.assertEqual((root / "target/package/nativepair/root/usr/bin/nativepair").stat().st_mtime, 1)


add_cases(BuildContracts, "Positive", "native_package_built", [
    ("metadata_version", ({}, (), 0)),
    ("explicit_version", ({"NATIVEPAIR_VERSION": "2.3.4-rc1"}, (), 0)),
    ("explicit_host_arch", ({"DEB_ARCH": run(["dpkg", "--print-architecture"]).stdout.strip()}, (), 0)),
], build)
add_cases(BuildContracts, "N1", "invalid_build_metadata_rejected", [
    ("invalid_version_" + str(index), ({"NATIVEPAIR_VERSION": version}, (), 1))
    for index, version in enumerate(("1", "1.2", "v1.2.3", "1.2.3/", "1.2.3;evil", "1.2.3\n", "NaN"))], build)
add_cases(BuildContracts, "N6", "wrong_build_arch_rejected", [
    ("unsupported_arch", ({"DEB_ARCH": "i386"}, (), 1)),
    ("foreign_arch", ({"DEB_ARCH": "arm64" if run(["dpkg", "--print-architecture"]).stdout.strip() == "amd64" else "amd64"}, (), 1)),
], build)
add_cases(BuildContracts, "N3", "cargo_build_failed", [
    ("compile_failure", ({"SYNTHETIC_BUILD_STATUS": "1"}, (), 1)),
], build)
add_cases(BuildContracts, "N12", "build_input_missing", [
    ("input_" + str(index), ({}, (path,), 1))
    for index, path in enumerate(("LICENSE", "NOTICE", "README.md", "target/release/nativepair", "target/release/nativepair-daemon"))], build)
