"""Independent tool, metadata, epoch and staging failure branches."""
from pathlib import Path
import shutil
import tempfile
import unittest

from scenarios import add_cases
from test_packaging_contract import REPO, archive, build_tree, checksum, run


TOOLS = ("cargo", "dpkg", "dpkg-deb", "python3", "sha256sum", "awk", "sed",
         "tr", "grep", "readlink", "basename", "dirname", "mktemp", "rm",
         "mkdir", "install", "du", "find", "touch", "tar")


def isolated_tools(root, missing=()):
    directory = root / "bin"
    directory.mkdir(exist_ok=True)
    for command in TOOLS:
        target = directory / command
        if command in missing:
            target.unlink(missing_ok=True)
        elif not target.exists():
            target.symlink_to(shutil.which(command))
    return str(directory)


def replace_tool(root, command, body):
    path = root / "bin" / command
    path.unlink(missing_ok=True)
    path.write_text("#!/bin/sh\n" + body + "\n")
    path.chmod(0o755)


class PackagingBranches(unittest.TestCase):
    pass


def build(self, value):
    missing, replacements, environment, expected, epoch = value
    with tempfile.TemporaryDirectory(prefix="nativepair-build-branch-") as directory:
        root = Path(directory)
        env = build_tree(root)
        env["PATH"] = isolated_tools(root, missing)
        env.update(environment)
        for command, body in replacements.items():
            replace_tool(root, command, body)
        if epoch == "absent":
            env.pop("SOURCE_DATE_EPOCH", None)
        elif epoch == "derived":
            env.pop("SOURCE_DATE_EPOCH", None)
            replace_tool(root, "git", "printf '2\\n'")
        if environment.get("NATIVEPAIR_ARTIFACTS_DIR") == "custom":
            env["NATIVEPAIR_ARTIFACTS_DIR"] = str(root / "custom-artifacts")
            env["NATIVEPAIR_PACKAGE_BUILD_DIR"] = str(root / "custom-staging")
        result = run(["/bin/bash", str(root / "scripts/build-deb.sh")], env=env)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        if expected in (130, 143):
            self.assertEqual(list((root / "artifacts").glob("*.deb")), [])
        if expected == 0:
            package = Path(result.stdout.strip().splitlines()[-1])
            self.assertTrue(package.is_file())
            validated = run(["/bin/bash", str(REPO / "scripts/verify-deb.sh"), str(package)])
            self.assertEqual(validated.returncode, 0, validated.stdout + validated.stderr)
            if epoch == "derived":
                self.assertEqual((root / "target/package/nativepair/root/usr/bin/nativepair").stat().st_mtime, 2)
            if environment.get("NATIVEPAIR_ARTIFACTS_DIR") == "custom":
                self.assertEqual(package.parent, root / "custom-artifacts")
                self.assertTrue((root / "custom-staging/root/usr/bin/nativepair").is_file())


add_cases(PackagingBranches, "N7", "build_dependency_missing", [
    (tool, ((tool,), {}, {}, 1, None))
    for tool in ("cargo", "dpkg", "dpkg-deb", "python3", "sha256sum")], build)
add_cases(PackagingBranches, "N6", "cargo_metadata_invalid", [
    ("metadata_" + str(index), ((), {"cargo": "printf '%s\\n' '" + text + "'"}, {}, 1, None))
    for index, text in enumerate(("malformed", "{}", '{"packages":[]}',
        '{"packages":[{"name":"other","version":"0.1.0"}]}',
        '{"packages":[{"name":"nativepair-core"}]}'))], build)
add_cases(PackagingBranches, "N12", "staging_or_archive_failed", [
    (tool, ((), {tool: "exit 1"}, {}, 1, None))
    for tool in ("rm", "mkdir", "install", "sed", "du", "touch", "dpkg-deb", "sha256sum")], build)
add_cases(PackagingBranches, "N8", "epoch_supported", [
    ("no_epoch_or_git", ((), {}, {}, 0, "absent")),
    ("derived_epoch", ((), {}, {}, 0, "derived")),
    ("empty_git_epoch", ((), {"git": "exit 1"}, {}, 0, "absent")),
], build)
add_cases(PackagingBranches, "Positive", "custom_directories_supported", [
    ("custom_directories", ((), {}, {"NATIVEPAIR_ARTIFACTS_DIR": "custom"}, 0, None)),
], build)
add_cases(PackagingBranches, "N1", "invalid_epoch_rejected", [
    ("epoch_" + str(index), ((), {}, {"SOURCE_DATE_EPOCH": text}, 1, None))
    for index, text in enumerate(("NaN", "PRIVATE_CONTACT", "999999999999999999999999999"))], build)

add_cases(PackagingBranches, "N9", "packaging_interrupted_before_build", [
    (signal, ((), {"cargo": 'if [ "$1" = metadata ]; then\nprintf \'%s\\n\' \'{"packages":[{"name":"nativepair-core","version":"0.1.0"}]}\'\nelse\nkill -' + signal + ' "$PPID"\nfi'}, {}, code, None))
    for signal, code in (("INT", 130), ("TERM", 143))], build)


def verify(self, value):
    missing, replacements = value
    with tempfile.TemporaryDirectory(prefix="nativepair-verify-branch-") as directory:
        root = Path(directory)
        package = archive(root)
        env = {"PATH": isolated_tools(root, missing), "LC_ALL": "C"}
        for command, body in replacements.items():
            replace_tool(root, command, body)
        result = run(["/bin/bash", str(REPO / "scripts/verify-deb.sh"), str(package)], env=env)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)


add_cases(PackagingBranches, "N7", "verify_dependency_missing", [
    (tool, ((tool,), {})) for tool in ("dpkg-deb", "sha256sum", "awk")], verify)
add_cases(PackagingBranches, "N12", "verify_storage_or_extract_failed", [
    (tool, ((), {tool: body})) for tool, body in (
        ("mktemp", "exit 1"),
        ("dpkg-deb", 'if [ "$1" = --extract ]; then exit 1; fi\nexec /usr/bin/dpkg-deb "$@"'))], verify)


def interrupted_verify(self, value):
    signal, code = value
    with tempfile.TemporaryDirectory(prefix="nativepair-verify-signal-") as directory:
        root = Path(directory)
        package = archive(root)
        binary = root / "package/usr/bin/nativepair"
        binary.write_text('#!/bin/sh\nkill -' + signal + ' "$PPID"\nexit 0\n')
        built = run(["dpkg-deb", "--root-owner-group", "--build", str(root / "package"), str(package)])
        self.assertEqual(built.returncode, 0, built.stderr)
        checksum(package)
        temporary = root / "tmp"
        temporary.mkdir()
        result = run(["/bin/bash", str(REPO / "scripts/verify-deb.sh"), str(package)],
                     env={"PATH": isolated_tools(root), "TMPDIR": str(temporary), "LC_ALL": "C"})
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        self.assertEqual(list(temporary.iterdir()), [])
        self.assertNotIn("verification passed", result.stdout)


add_cases(PackagingBranches, "N9", "packaging_interrupted_during_verify", [
    (signal, (signal, code)) for signal, code in (("INT", 130), ("TERM", 143))], interrupted_verify)
