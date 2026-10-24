# NativePair Agent Guide

This file is the repository-level source of truth for automated development work.

## Operating rules

1. Read relevant documentation before changing code.
2. Classify work as either feature/refactor work or testing work.
3. For significant architecture, public API, data-model, security-boundary, or material UI/UX decisions, document options and obtain an explicit decision before implementation.
4. For reversible implementation details, decide autonomously, document the rationale where useful, and keep scope narrow.
5. Update documentation before code when behavior, architecture, or invariants change.
6. Keep commits atomic and use English Conventional Commit messages.
7. Never weaken tests to match defective behavior.
8. Prefer dependency injection and explicit interfaces over global state.
9. Never log message bodies, contact data, notification contents, phone numbers, or other personal payloads in normal diagnostics.
10. Keep the repository recoverable: another engineer should be able to continue from committed code and documentation alone.

## Branch policy

- Work lands on `dev`.
- `main` is updated only from a green, reviewed `dev` state.
- Long-lived branches are limited to `main` and `dev`.

## Current project phase

The current phase is protocol feasibility and foundation work. Do not build product UI around an unverified capability.

## Required reading

- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
- `docs/TESTING.md`
- `docs/PRIVACY.md`
- `docs/DECISIONS.md`

## Repository housekeeping — 2026-10-24

Mode A, documentation/ignore maintenance only. Baseline
`8051c48745b2583e3f4c2d3ed70fc6fa8d9a1e2f` on clean synchronized `dev`.
No product, architecture, protocol, privacy, audio, test or deployment change.

1. [x] Read project rules, canonical product/architecture/privacy/testing owners,
   M1 evidence/branch/coverage and hardware handoffs, scripts and actual CI.
2. [x] Add a docs navigation index grouped by protocol, audio, process/packaging
   and hardware. Map every original M1 branch-map artifact/anchor without
   reducing its exhaustive assertions, negative/interaction or mutation evidence.
3. [x] Qualify README/build/testing/CI text against the implemented workflow:
   ordinary Rust/syntax checks versus full binary-dependent contracts/package
   checks on an annotated current-main tag. Keep original paragraphs and dated
   failure/acceptance bodies verbatim behind explicit historical boundaries.
4. [x] Add local assistant-state ignores; existing IDE/build/work/artifact rules
   remain. No disposable tracked IDE/model preset or diagnostic file was found.
   Preserve all hardware records, canonical inventories, release/build scripts,
   code/tests/config/lock and ignored sole-copy captures/packages.
5. [x] At final gate run existing pure graph-parser and hermetic GetCalls
   contracts once, plus source/hash/body/link/anchor/catalog/ignore/diff checks.
   No actual Bluetooth/D-Bus/PipeWire/journal/device/call/SMS/probe, Rust build,
   package install or process-stability campaign is needed for documentation.
   Commit docs/config separately; normal push dev after fresh fetch, no main
   promotion, release tag, hardware action or external publication.

Risks: treating endpoint/graph evidence as audible physical uplink, old counts
as new coverage, or synthetic command tests as real phone operations. Preserve
all original M1 maps/inventory/negative evidence and distinguish exact source,
automated proof and remaining physical acceptance. Original failed call probes
and fresh-approval boundaries remain. Rollback uses inverse scoped commits,
not shared history rewrite; no data, device, audio or artifact undo is needed.

Final housekeeping evidence: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest
discover -s scripts/tests -p test_audio_graph.py -v` exits0,41 tests;
the same command with `-p test_getcalls_compatibility.py` exits0,84 tests.
Both existing suites ran once; all125 cases passed. GetCalls uses hermetic
external-command fakes, not actual phone/D-Bus/PipeWire calls.
External static checks exit0:700 checks,304 local links,23 branch-map sections,
109 protected original SHA-256 values identical. Canonical1869-method inventory
and182-case process lane remain unchanged; their old execution is not a fresh
coverage/stability result. All original M1 maps, hardware evidence and receipt
JSON remain intact. `git diff --check 8051c48745b2583e3f4c2d3ed70fc6fa8d9a1e2f HEAD`
exits0. No full Rust/Python/10x/mutation/package/install/remote-CI or hardware
acceptance was executed. Physical microphone/uplink, ANCS and recovery gates
remain open. All owned commands completed; no background process needs cleanup.
