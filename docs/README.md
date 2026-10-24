# NativePair documentation navigation

This index links existing owners and evidence; it is not another architecture,
live device-state inventory or test-completion claim. Start with
[agent rules](../AGENTS.md), [roadmap](ROADMAP.md), [architecture](ARCHITECTURE.md),
[privacy](PRIVACY.md) and [decisions](DECISIONS.md). M1 remains in progress;
no GUI, platform parity or unsupported protocol capability is implied.

## Owners and current boundaries

| Area | Read first | Evidence and remaining boundary |
| --- | --- | --- |
| Product and feasibility | [Root README](../README.md), [feasibility](FEASIBILITY.md), [capability matrix](CAPABILITY_MATRIX.md) | Observed Pixel MAP/PBAP/HFP results are device/environment-bound; iPhone ANCS and wider recovery remain open. |
| Automated verification | [Testing](TESTING.md), [M1 execution](M1_AUTOMATED_VERIFICATION.md), [branch map](M1_BRANCH_MAP.md), [coverage map](M1_COVERAGE_MAP.md) | Exact methods, categories, assertion/mutation and process-lane counts retain their units and source versions; no new coverage inferred. |
| Forecast versus executable inventory | [Original M1 matrix](TEST_MATRIX_M1.md), [canonical 1,869-method inventory](evidence/m1-automated-test-inventory.json), [182-case process lane](evidence/m1-process-stability-inventory.json) | The original ~196/~40 estimate is planning, not the implemented method count or hardware proof. |
| Wire and call-state safety | [GetCalls correction](M1_GETCALLS_COMPATIBILITY.md), [HFP node classification](M1_HFP_NODE_CLASSIFICATION.md) | Preserve dictionary/legacy replies, fail-closed unknown state, no pre-existing-call mutation and bounded owned-call cleanup. |
| Physical HFP audio | [Audio continuation](M1_HFP_AUDIO_NEXT.md), [passive uplink](M1_HFP_UPLINK_OBSERVATION.md), [optional watcher](CALL_AUDIO_WATCH.md) | Endpoint presence/direct graph links are not audible signal or physical microphone identity; any new real call needs fresh explicit approval. |
| Hardware record | [Pixel evidence](evidence/pixel-6a-2026-10-06.md), [capability matrix](CAPABILITY_MATRIX.md) | Preserve failed probes, game-focus confound, partial recovery, wired-headphone/internal-mic observations and unanswered live uplink. |
| Build and CI | [Packaging](BUILD_AND_PACKAGING.md), [CI cadence/known failure](CI_RELEASE_GATES_2026-10-18.md), [workflow source](../.github/workflows/ci.yml) | Branch Rust/syntax differs from tagged binary-dependent Python/package/install/upload; no new release tag or host install for docs. |
| Governance | [Contributing](../CONTRIBUTING.md), [security](../SECURITY.md), [changelog](../CHANGELOG.md), [headless ADR](adr/0001-headless-rust-daemon.md), [license ADR](adr/0002-apache-2-license.md) | Preserve local privacy, daemon ownership and material architecture approval. |

## Exhaustive branch-map navigation by subsystem

All original M1 maps and evidence remain unchanged. Every artifact section in
the existing branch map is linked below, including packaging, process cleanup,
protocol, audio and thin binary contracts. Original branch/interaction tables
remain authoritative; this index does not sample or replace their assertions.

### Daemon and CLI

- [crates/nativepair-core/src/lib.rs](M1_BRANCH_MAP.md#cratesnativepair-coresrclibrs)
- [crates/nativepair-cli/src/main.rs](M1_BRANCH_MAP.md#cratesnativepair-clisrcmainrs)
- [crates/nativepair-daemon/src/main.rs](M1_BRANCH_MAP.md#cratesnativepair-daemonsrcmainrs)

### Packaging and process ownership

- [scripts/build-deb.sh](M1_BRANCH_MAP.md#scriptsbuild-debsh)
- [scripts/verify-deb.sh](M1_BRANCH_MAP.md#scriptsverify-debsh)

### Bluetooth, OBEX and messages

- [scripts/probe-bluetooth.sh](M1_BRANCH_MAP.md#scriptsprobe-bluetoothsh)
- [scripts/probe-map-events.sh](M1_BRANCH_MAP.md#scriptsprobe-map-eventssh)
- [scripts/probe-map-sdp.sh](M1_BRANCH_MAP.md#scriptsprobe-map-sdpsh)
- [scripts/probe-map-send.sh](M1_BRANCH_MAP.md#scriptsprobe-map-sendsh)
- [scripts/probe-mns.sh](M1_BRANCH_MAP.md#scriptsprobe-mnssh)
- [scripts/probe-obex-read.sh](M1_BRANCH_MAP.md#scriptsprobe-obex-readsh)
- [scripts/probe-obex-session.sh](M1_BRANCH_MAP.md#scriptsprobe-obex-sessionsh)
- [scripts/probe_obex_monitor.py](M1_BRANCH_MAP.md#scriptsprobe_obex_monitorpy)

### Audio, HFP and call safety

- [scripts/probe-audio-health.sh](M1_BRANCH_MAP.md#scriptsprobe-audio-healthsh)
- [scripts/probe-audio-routing.sh](M1_BRANCH_MAP.md#scriptsprobe-audio-routingsh)
- [scripts/probe-call-audio-watch.sh](M1_BRANCH_MAP.md#scriptsprobe-call-audio-watchsh)
- [scripts/probe-hfp.sh](M1_BRANCH_MAP.md#scriptsprobe-hfpsh)
- [scripts/probe-hfp-audio.sh](M1_BRANCH_MAP.md#scriptsprobe-hfp-audiosh)
- [scripts/probe-hfp-call.sh](M1_BRANCH_MAP.md#scriptsprobe-hfp-callsh)
- [scripts/probe-hfp-sco.sh](M1_BRANCH_MAP.md#scriptsprobe-hfp-scosh)
- [scripts/probe_call_audio_watch.py](M1_BRANCH_MAP.md#scriptsprobe_call_audio_watchpy)
- [scripts/probe_audio_graph.py](M1_BRANCH_MAP.md#scriptsprobe_audio_graphpy)
- [scripts/probe_hfp_uplink.py](M1_BRANCH_MAP.md#scriptsprobe_hfp_uplinkpy)

## Source-bound machine-readable receipts

- [Initial execution](evidence/m1-automated-execution.json), [source trace](evidence/m1-automated-source-trace.json) and [mutation results](evidence/m1-automated-mutations.json): original baseline counts/observations.
- [GetCalls execution](evidence/m1-getcalls-execution.json) and [mutations](evidence/m1-getcalls-mutations.json): actual wire-shape correction.
- [Node-classification execution](evidence/m1-hfp-node-execution.json): source 39172c9, full 1,665-method pass and separate process-stability evidence.
- [Direct-uplink execution](evidence/m1-hfp-uplink-execution.json): source 051cc07, full 1,869-method pass and 13 new assertion-killed mutations; retained prior 182-case lane proof.

These are historical exact-source receipts, not a fresh execution, new CI result,
zero-flakiness guarantee or live-device permission. Ignored `work/` and
`artifacts/` may contain sole-copy traces or packages; they are not disposable
because ignored. Documentation cleanup does not read or erase them.
