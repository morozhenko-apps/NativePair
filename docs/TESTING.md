# Testing Strategy

## Purpose

Tests protect behavior, protocol contracts, privacy invariants, and state transitions. Coverage percentage is not a goal by itself.

## Test pyramid

Preferred distribution:

- 70-80% unit/domain;
- 15-25% integration/contract;
- 5-10% end-to-end or hardware smoke tests.

Hardware-dependent tests are not substitutes for deterministic domain and adapter tests.

## Required qualities

Tests must be:

- deterministic;
- order-independent;
- explicit about final state and side effects;
- free from arbitrary sleeps;
- based on fakes/adapters for external services;
- strong enough to fail when meaningful domain behavior is mutated.

## Priority risk areas

- capability-state transitions;
- reconnect and service restart behavior;
- malformed protocol payloads;
- permission revocation;
- duplicate/replayed events;
- concurrency between discovery/session teardown;
- stale device state;
- personal data leakage in logs;
- persistence migration if sensitive caching is ever introduced.

## Protocol fixtures

Protocol fixtures must use synthetic data. Never commit real:

- message bodies;
- phone numbers;
- contacts;
- call history;
- notification text;
- Bluetooth identifiers tied to a user's device.

## CI baseline

Every code change must pass:

```bash
cargo fmt --all -- --check
cargo clippy --workspace --all-targets --all-features -- -D warnings
cargo test --workspace --all-features
```

Repository shell scripts are syntax-checked in CI. Debian packaging is also built and verified in CI so packaging regressions fail before release work.

## Packaging verification

The Debian package gate validates:

- package name/version/architecture;
- required binary locations;
- project documentation and license payload;
- executable smoke via packaged `nativepair --version` and daemon `--version`;
- SHA-256 sidecar integrity.

The package gate is an integration/contract check, not a substitute for daemon or protocol tests.

## HFP mutation-probe contract tests

HFP real-call probes are never exercised against hardware in CI. Synthetic external-command adapters model `bluetoothctl` and `busctl` for the actual scripts, covering no-call preflight, pre-existing-call rejection, successful dial/hangup, ambiguous Dial failure after side-effect, and SCO activation failure cleanup. Test fixtures must contain only placeholder addresses/numbers and assert that no dialed number appears in stdout/stderr.

The complete deterministic Python suite runs once per dev CI pass, without requiring a Bluetooth controller or real test recipient. The automatic SCO transport cases are synthetic; they do not establish live Pixel behavior. The run also checks script syntax and preserves the existing packaging gate.

The central safety invariant: once a guarded `Dial` has been attempted, a probe must make a bounded `HangupAll` cleanup attempt if no explicit successful hangup was already performed, even when the Dial method reply is missing or fails. Calls are not created by CI.

## M1 Mode B planning baseline

The provisional scenario counts, interaction matrix, N1–N12 plan and local Ubuntu + ADB automation forecast are recorded in [M1 Mode B Test Matrix and Local ADB Automation Plan](TEST_MATRIX_M1.md). They are estimates, not measured coverage, and must be reconciled with a complete per-file inventory.

The current executable inventory and results supersede the synthetic forecast:
[M1 automated verification execution record](M1_AUTOMATED_VERIFICATION.md).
Build the actual binary entry points before running Python integration tests:

```bash
cargo build --workspace --locked
python3 scripts/tests/run_suite.py
```

The runner prints progress, exact primary-category counts and optional canonical
scenario IDs (`--inventory <path>`). Every negative case also asserts cleanup
and privacy where applicable, without counting those assertions again. For the
required stability gate, execute fresh suites sequentially:

```bash
python3 scripts/tests/run_suite.py --runs 10 --report work/repeated-runs.json
python3 scripts/tests/review_mutations.py --output work/mutation-review.json
```

`--trace-first` on the ten-run command adds source-line/arc evidence for its first
run only. Trace files and detailed local logs live under ignored `work/`; final
summary evidence and the canonical inventory belong in `docs/evidence/`.
Mutation trials use disposable copies, verify an unmodified baseline for each
trial and require assertion failures; compile/import errors are not kills.

Python requires only its standard library. Native packaging fixtures also
require existing `dpkg`, `dpkg-deb`, `sha256sum` and `tar`. Probe fixtures use an
allowlisted PATH; Bluetooth/D-Bus/PipeWire/OBEX/journal commands are synthetic.
No hardware E2E test runs in CI or in this stability gate. Test-owned process
groups and temporary directories are removed after each scenario. Pure parser
and observer tests use fake command adapters and clocks; the core remains
independent of transport dependencies.

## Hardware verification

Hardware tests must document:

- device model;
- OS version;
- Linux distribution;
- BlueZ version;
- relevant permissions;
- exact capability being verified;
- evidence level from `docs/FEASIBILITY.md`.

Logs included in issues or test evidence must be sanitized before publication.
