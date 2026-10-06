# Build and Packaging

## Goals

NativePair should be straightforward to build on Ubuntu and should produce a real Debian package without requiring Node.js, WebKit, Tauri, or an application framework solely for packaging.

Packaging is introduced early even though the full desktop product belongs to M6. The purpose is to catch release-layout and dependency mistakes before the daemon and GUI become large.

## Patterns reviewed in sibling repositories

Two existing project patterns informed this baseline:

- Picturix uses explicit quality gates, release preflight validation, checksums, and artifact verification. Its current Linux desktop distribution is AppImage plus a CLI archive.
- rQuickShare uses Tauri's Linux bundler, which can emit Debian packages as part of its application bundle.

NativePair does not use Tauri, so its Debian package is built directly with Debian tooling.

## Local quality gate

```bash
cargo fmt --all -- --check
cargo clippy --workspace --all-targets --all-features -- -D warnings
cargo test --workspace --all-features
```

## Debian package

Build:

```bash
./scripts/build-deb.sh
```

Verify an existing package:

```bash
./scripts/verify-deb.sh artifacts/nativepair_<version>_<arch>.deb
```

The build script:

1. builds locked release binaries;
2. creates a clean package root;
3. installs the CLI as `/usr/bin/nativepair`;
4. installs the daemon binary as `/usr/libexec/nativepair-daemon`;
5. installs project license/notice/readme documentation;
6. emits a Debian control file;
7. builds the package with `dpkg-deb`;
8. writes a neighboring SHA-256 sidecar.

The package deliberately does **not** install or enable a systemd user service yet. Service activation belongs to the D-Bus/daemon milestone after the daemon contract is real.

## Runtime dependencies

The package declares BlueZ and BlueZ OBEX support because they are core runtime services for the planned baseline integration.

Call-audio dependencies are not declared yet. HFP/PipeWire/WirePlumber/oFono requirements must be determined from M1 evidence before they become package contracts.

## CI package gate

CI must:

- run the Rust quality gate first;
- syntax-check repository shell scripts;
- build the Debian package;
- verify package metadata and file layout;
- extract the package and smoke the packaged binaries;
- verify the SHA-256 sidecar;
- upload the `.deb` and checksum as a CI artifact.

A package produced by a red quality gate is not a valid artifact.
