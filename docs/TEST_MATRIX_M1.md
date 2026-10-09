# M1 Mode B Test Matrix and Local ADB Automation Plan

Status: **provisional planning baseline, NOT measured coverage**
Date: **2026-10-08**
Scope: **M1 protocol feasibility**, not the full M2–M7 product.
Working branch: **dev**; main is not promoted on projections.

This document preserves the initial planning estimate. A full Repository Scan, per-production-file Branch Map, exhaustive inventory, mutation review and measured coverage are **still required**. Counts below may change. Never present planned scenario counts as executed tests, coverage percentage, or proven device features.

The automated implementation now has its own execution record and canonical
inventory in [M1 automated verification](M1_AUTOMATED_VERIFICATION.md). This
document remains a historical hardware/automation forecast; use that execution
record for current synthetic counts, mutations and stability-gate results.

Related records: [Testing Strategy](TESTING.md), [Feasibility](FEASIBILITY.md), [Capability Matrix](CAPABILITY_MATRIX.md), [Roadmap](ROADMAP.md), [Pixel hardware evidence](evidence/pixel-6a-2026-10-06.md).

## Verified baseline (as of this snapshot)

Exactly **22 automated test methods** are present:
- **5** Rust unit tests covering capability availability/state in the core crate;
- **5** Python unit tests for the passive call-audio watcher;
- **12** Python synthetic contract tests running the guarded HFP/SCO Bash probes against fake Bluetooth/D-Bus commands.

Additional checks run in CI but are not counted as test methods: Rust fmt/clippy, Bash syntax/executable bits, Debian package build/verify/install, binary smoke. The latest inspected dev baseline at commit 423fd40 had green CI.

Hardware outcomes are a different metric. Pixel 6a has proven MAP message list/read, SMS send and incoming MNS events, PBAP listing, HFP Dial/Hangup control. SCO transport activation and bidirectional audio **via the Linux headset and microphone** remain unproven. iPhone ANCS has no hardware evidence yet.

**Do not compute 22 / 196 as a coverage ratio.** A test method and a unique scenario are not interchangeable units; code/branch coverage also has an entirely different denominator.

## Provisional total: ~196 distinct M1 scenarios

| Subsystem | Estimated scenarios | Evidence level / remaining work |
| --- | ---: | --- |
| Bluetooth pairing, identity, permissions | 20 | Baseline paired/trusted, more failure cases pending |
| MAP SMS read/list | 22 | Positive path proven |
| MAP SMS send and MNS events | 30 | Positive paths proven |
| PBAP contacts | 18 | Positive path proven |
| HFP call control and states | 24 | Dial/Hangup proven |
| SCO audio routing and recovery | 29 | Preflight + active call state; Linux duplex route not proven |
| Cross-cutting recovery, privacy, packaging | 25 | Some CI/safety evidence, broader coverage pending |
| iPhone ANCS, BLE, permissions | 28 | No iPhone hardware result |
| **Total** | **196** | **Estimate only** |

The 196 is the *estimated number of unique candidate scenario IDs across M1*. Assign each real scenario one canonical ID; link it to all affected production files and categories rather than counting it multiple times. Some rows cross functional boundaries; the separately described interaction count is **a subset** of 196.

Provisional environment allocation: **110** Linux synthetic/contract scenarios, **58** Pixel hardware-dependent scenarios, and **28** iPhone hardware-dependent scenarios. These sum to 196 but must be validated by the exhaustive inventory.

## Positive / N1–N12 matrix

These names are **initial NativePair candidate mappings**, not a universal standardized taxonomy. Reconcile with the latest project-approved Mode B SSOT before freezing IDs. If a negative category cannot apply, record N/A with an explicit rationale.

| Matrix class | Test intent |
| --- | --- |
| Positive | Valid operation, state and cleanup |
| N1 | Bad UUID/profile/device identifier and malformed fields |
| N2 | Empty lists, data limits, boundaries, oversized payload |
| N3 | Timeout, transient error, retries, retry exhaustion |
| N4 | Replay, duplicate events, SMS idempotency |
| N5 | Concurrent sessions, HFP/SCO races, cancellation |
| N6 | Stale D-Bus call/session object and malformed OBEX response |
| N7 | Pair/trust/permission revocation, denial and locked phone |
| N8 | Event ordering, timestamps/timezones where relevant |
| N9 | Interrupt, disconnect, restart, cleanup |
| N10 | Privacy redaction, no names/numbers/bodies in logs |
| N11 | Billing / entitlement: **N/A for M1** |
| N12 | Temp files, read-only filesystem, disk-full and error cleanup |

Branch mapping must determine which cases actually exist in production. Never add fictitious variants to reach a target test number.

## Interaction matrix: ~40 scenarios WITHIN 196

Estimate: **about 28–30 pairwise** and **10–12 high-risk higher-order** interactions. The ranges are approximate and must be de-duplicated, not summed on top of 196. Focus on shared state, side effects and cross-profile failures; do not attempt full Cartesian combinations.

Illustrative candidates, **not tests already implemented**:

| Candidate | Interacting factors | Core assertion |
| --- | --- | --- |
| IM-01 | MAP session + HFP incoming call | No corrupted transport state |
| IM-02 | MAP send + Bluetooth drop + retry | No duplicate SMS |
| IM-03 | MNS event + MAP refresh | Correct event ordering/deduplication |
| IM-04 | PBAP session + phone locked + permission revoked | Proper failure/authorization handling |
| IM-05 | HFP active call + PipeWire restart | Cleanup/recovery |
| IM-06 | SCO pending + duplicate Activate | No destructive transport race |
| IM-07 | Call active + call object path replaced | Fresh state read, no stale-object hang |
| IM-08 | SCO active + route change + hangup | No orphan nodes/default-route corruption |
| IM-09 | MAP active + call incoming + Pixel locked | Correct permission/priority behavior |
| IM-10 | SMS send + disconnect + service restart | Bounded retry/idempotency |
| IM-11 | MNS registration + obexd restart + reconnect | Resubscription without duplicate events |
| IM-12 | Protocol operation pending + disconnect + daemon teardown | Bounded cleanup, no sensitive leakage |

Some full-product assertions depend on daemon implementation in M2–M4. M1 can characterize host/platform feasibility, but tests of unimplemented future features should be assigned to the corresponding future milestone, not falsely reported as failed M1 tests.

## What a local Ubuntu agent with ADB can automate

**Assumptions:** an authorized agent runs on the Ubuntu host, can invoke BlueZ, obexd, PipeWire and CI commands, and can observe a user-authorized Pixel 6a through ADB. ADB alone is not Bluetooth transport control.

Forecast after the tests and hooks have been built:

| Test execution environment | Estimated scenarios | Potentially automated locally |
| --- | ---: | ---: |
| Linux deterministic unit/contract | 110 | 110 |
| Pixel 6a + BlueZ/PipeWire + ADB | 58 | approximately 40–47 |
| iPhone ANCS via ADB | 28 | 0 |
| **Total** | **196** | **approximately 150–157** |

Thus forecast local automation of the M1 plan is **150–157 / 196 = approximately 77–80%**. Within the Pixel hardware group, **40–47 / 58 = approximately 69–81%** may be scripted. A rough **70–80% reduction in repeat manual Pixel interactions** is a hypothesis, not observed time saved. Record actual manual steps and durations before making a measured time-saving claim.

This is **not** current code coverage, branch coverage, mutation score, completion percentage or currently running automation. Nor does it imply that all 110 Linux scenarios already have tests.

ADB can observe many Android diagnostics and may automate accessible UI/state operations, but permissions, non-root restrictions, Android version, OEM behavior and physical Bluetooth/audio devices limit it. ADB cannot replace human speech/hearing verification, a remote participant, all Android consent prompts, or iPhone hardware. Logging sensitive Android dumps or audio is not permitted in CI fixtures or evidence.

Mandatory manual or separate-device gates include: correct physical Linux **microphone** and **headphones** during a real call (not merely voice audible on the Pixel), duplex intelligibility/latency, audible glitches, remote recipient confirmation, user consent to real calls/SMS, irreversible/permission changes, and iPhone ANCS tests.

**Authorization invariant:** local availability of ADB does not authorize real calls, SMS sends, phone reboots, pairing removal, permission changes or disruptive service restarts. Require explicit per-experiment approval and privacy-safe output. Never log or commit real phone numbers, addresses, contacts, message bodies, speech recordings or raw dumps containing personal data.

## Mode B required artifacts and completion gate

1. **Repository Scan:** production-file inventory, modules, integration surfaces, CI.
2. **Risk & Invariant Analysis:** transport, privacy, idempotency, call ownership, crash/cleanup, permission and audio routing risks.
3. **Exhaustive Test Inventory:** one unique scenario ID, file owner, preconditions, expected output, environment and verification state.
4. **Branch Map:** all production branches and meaningful errors/recovery exits; explicit untested branches.
5. **Positive/N1–N12 Test Matrix:** applicability and evidence per branch.
6. **Interaction Matrix:** risk-driven pairwise and higher-order cases, counted as a subset of unique scenarios.
7. **Coverage Estimation and per-production-file Coverage Map:** instrumented line/branch results separately from projections; exclusions justified.
8. **Implementation:** deterministic tests and mocks plus approved manual hardware smoke.
9. **Mutation Review:** surviving mutations in critical invariants documented and addressed.
10. **Execution:** local and CI results, Android/iPhone environment details and sanitized evidence.
11. **Completion Gate:** risk-significant branches tested, expected checks green, remaining hardware support clearly marked proven/unknown/blocked.

Execution cadence, refined by the user on 2026-10-09: static checks and all
deterministic contracts run once. The 182-scenario process stability lane runs
ten times (the complete baseline includes its first pass). This lane tests
actual subprocess, FIFO, signal and teardown interactions. No observed flaky
tests are being accepted. CI runs the complete suite once per change; the local
runner records both lane inventories and all pass/failure results. Hardware
verification remains separate and is not performed in CI.

## Updating this plan

Replace estimates with measured status fields: planned, implemented, CI verified, Pixel hardware verified, iPhone hardware verified, human-confirmed, blocked or N/A. Track unique test IDs and intersections without double-counting. Report actual line/branch/mutation coverage with a named denominator, tool/run reference and date. Link sanitized hardware reports and CI. If M1 scope changes, revise both estimates and assumptions. Do not promote to main merely because an estimate suggests high coverage.
