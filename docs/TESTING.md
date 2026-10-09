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
required stability gate, execute one complete baseline followed by nine fresh
process stability runs:

```bash
python3 scripts/tests/run_suite.py --runs 10 --report work/repeated-runs.json
python3 scripts/tests/review_mutations.py --output work/mutation-review.json
```

`--runs 10` executes Rust and all Python contracts once. The first full run
counts as the first pass of the 182-scenario process stability lane; runs 2–10
execute only that lane. Formatting, Clippy, syntax, packaging, pure parsers,
observer fake-clock cases and other deterministic scenarios are not repeated.
The lane contains OBEX session/FIFO/cleanup contracts (109), MAP sending (26),
MAP event subprocess contracts (15), probe interruption cases (24), HFP owned
call interruption cases (4) and packaging interruption cases (4). Its exact IDs
are recorded in `work/stability-inventory.json`. This selection is based on
process interactions; no observed flaky test is being excused or excluded.
Use `--lane process-stability --runs 10` to repeat only that lane after an
independently completed full baseline. CI runs all contracts once.

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

## GetCalls wire regression

The Pixel hardware continuation revealed the dictionary GetCalls signature
`a{oa{sv}}`; default fixtures now use it. Explicit legacy and dictionary rows
are in `test_getcalls_compatibility.py`. Run the scoped regressions with:

```bash
python3 -m unittest discover -s scripts/tests -p test_getcalls_compatibility.py -v
python3 scripts/tests/review_mutations.py --start-at call_dictionary_reply_rejected --output work/getcalls-mutations.json
```

The GetCalls-revision inventory contained 1447 Python methods. The previous ten-run
process stability evidence is tied to commit 5d72c31; the wire correction does
not change process/signal ownership logic and receives one fresh full-suite
run plus six targeted mutation trials. See [the correction record](M1_GETCALLS_COMPATIBILITY.md).

## HFP gateway node regression

The current inventory contains 1665 Python methods, including 218 explicit
profile/class/direction/default-device and early-hangup observation rows in
`test_hfp_node_classification.py`. Only the external command adapters are fake;
SCO/routing/health scripts and shared classification execute unchanged.

```bash
python3 -m unittest discover -s scripts/tests -p test_hfp_node_classification.py -v
python3 scripts/tests/review_mutations.py --start-at hfp_gateway_profile_ignored --output work/hfp-node-mutations.json
```

Source rationale, complete changed-artifact inventory, negative/interaction
matrix and execution state: [HFP node correction](M1_HFP_NODE_CLASSIFICATION.md).
Full-suite and process-only stability evidence are recorded there separately.
A failed node wait now records fresh anonymous call/transport states before
cleanup; `unknown` never means an absent call. This does not establish the
timing of the earlier live attempt or authorize a new call.

## Direct HFP microphone-link observation

The next addition contains 203 direct-uplink contracts plus one mutation-runner
bytecode regression (204 new methods; 1869 Python methods in total). Run the
scoped contracts and 13 targeted mutations with:

```bash
python3 -m unittest discover -s scripts/tests -p test_hfp_uplink.py
python3 -m unittest discover -s scripts/tests -p test_mutation_execution.py
python3 scripts/tests/review_mutations.py --start-at uplink_foreign_target_included --output work/uplink-mutations.json
```

The observer never calls or alters audio. Direct active graph links are evidence
of connection only, not proof of audible signal or physical microphone identity.
Plan, inventory, limits and execution: [uplink observation](M1_HFP_UPLINK_OBSERVATION.md).
Mutation Python subprocesses disable bytecode writes in fresh disposable trees,
so equal-length edits with equal mtimes cannot silently reuse baseline bytecode.

For source 39172c9, the complete 1665-method suite passed once and the existing
182-case process lane passed nine further runs: ten successes including the
baseline, with zero observed flakes. Static/Rust/pure cases were not repeated.
Results and source hashes: [execution artifact](evidence/m1-hfp-node-execution.json).
