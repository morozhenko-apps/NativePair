# HFP node classification and early-hangup diagnostics

Date: 2026-10-09. Mode B: regression verification and exposed-defect correction.

## Analysis and limits

The approved Pixel call reached active SCO and the user confirmed computer
output and microphone. The probe counted zero endpoints. It inspected endpoints
before its own HangupAll cleanup, but a remote/manual hangup during the bounded
wait could remove them. No contemporaneous unfiltered graph or end-of-wait call
state was retained. The historical cause cannot be established from that run.

A separate classifier defect is reproducible from source: all four audio
consumers accept only headset-head-unit. Installed PipeWire is 1.6.2. Upstream
[profile names](https://github.com/PipeWire/pipewire/blob/1.6.2/spa/plugins/bluez5/defs.h)
distinguish headset-audio-gateway. Its
[source](https://github.com/PipeWire/pipewire/blob/1.6.2/spa/plugins/bluez5/media-source.c)
and [sink](https://github.com/PipeWire/pipewire/blob/1.6.2/spa/plugins/bluez5/media-sink.c)
implementations can expose Stream/Output/Audio and Stream/Input/Audio.
Default devices and telephony streams have different media classes.

## Decision, invariants and scope

Use two pure shared helpers in probe_audio_graph.py: is_hfp(props) recognizes
exactly the two supported profile names; hfp_direction(props) returns source,
sink or None. Audio/Source and Audio/Sink retain their meanings for both
profiles. Only gateway Stream/Output/Audio is downlink (source at the Bluetooth
boundary); only gateway Stream/Input/Audio is uplink (sink at that boundary).
Internal/unknown classes never prove duplex. These are node observations, not
proof of running links, audibility or repeatability. Keep distinct valid IDs,
exact target address matching, both-direction readiness and privacy guards.

Routing source/sink presence includes gateway streams, but default device
checks still require actual Audio/Source or Audio/Sink; streams cannot prove a
phone default device. Health and passive observer counts recognize both
profiles without changing their existing media-class or link semantics.

On failed node readiness, record fresh anonymous call_state_after_node_wait
(active/dialing/alerting/incoming/waiting/held/disconnected/absent/unknown) and
transport_state_after_node_wait (idle/pending/active/error/unknown), before
cleanup. Only a canonical successful empty GetCalls means absent. Malformed or
failed reads mean unknown. Preserve hfp_nodes_not_ready failure, all existing
wait limits, cleanup, no-call guard and activation behavior. End snapshots are
sequential observations, not an atomic timeline or proof of which event came
first. No new call, routing mutation, service restart, API or dependency.

## Complete scoped inventory and branch map

Existing strict-decoder, malformed-graph, distinct-ID, privacy, ownership,
interruption and activation inventories remain applicable. New artifacts and
all changed executable branches are inventoried before tests:

| Artifact | Branches / explicit planned cases | Level | Risk / rationale |
| --- | --- | --- | --- |
| is_hfp + hfp_direction | Exact two profiles versus missing, empty, A2DP, unknown, case mismatch, suffix, list, dict and integer; each crossed with source/sink, output/input streams, two Internal classes, unknown, missing, empty, list, dict, integer | Unit | High: false absence or false duplex; 132 rows |
| SCO + routing consumers | Three profile/class families (head-unit physical, gateway physical, gateway streams), each in SCO and routing: duplex, source only, sink only, repeated source, repeated sink, duplicate ID, wrong target, unknown roles; physical versus stream default checks | Contract | High: preserve distinct directions and target; 48 rows |
| health + watcher consumers | Both profiles and unrelated A2DP, with real graph/count assertions | Contract / Unit | Medium: consistent profile counts; 6 rows |
| failed SCO node wait | active/absent/disconnected/unknown call crossed with idle/pending/active/error/unknown/failed transport; other five call states; malformed/failed call query; legacy canonical empty | Contract | High: separate observed hangup from unknown; 32 rows |

Expected addition: 218 scenarios. Count reconciliation is required before
completion; exact canonical IDs are the final inventory. Nonmatching profile
and malformed property rows are N6; missing direction/duplicate ID N2;
foreign target N7; lifecycle interactions N9/N5; query failures N3; normal
classification Positive. Every shell row checks privacy and temporary cleanup,
plus exactly one owned Dial and HangupAll for SCO, or zero mutations for passive
probes. No domain subject is mocked; only external commands are synthetic.

## Negative matrix and interactions

| Artifact | Positive | N1 | N2 | N3 | N4 | N5 | N6 | N7 | N8 | N9 | N10 | N11 | N12 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| shared classifier | Covered | Covered via N6 types | Covered via N6 missing | NA pure | NA pure | NA pure | Covered exhaustive product | NA no identity | NA no dates | NA pure | Existing + no output | NA no billing | NA pure |
| SCO/routing | Covered | Existing | Covered | Existing | Existing one Dial | Existing | Covered | Covered | NA no dates | Existing | Covered cross-cutting | NA no billing | Existing + cleanup |
| health/watcher | Covered | Existing | Existing | Existing | NA read-only | Existing | Covered | NA no auth changes | NA no dates | Existing | Existing | NA no billing | Existing |
| end-of-wait observations | Covered active call | NA enums | Covered absent | Covered | Existing cleanup once | Covered combinations | Covered unknown | Existing guards | NA no dates | Covered early hangup | Covered cross-cutting | NA no billing | Existing cleanup |

## Milestones, risks and rollback

1. Commit this analysis, inventory, decisions and plan before tests/code.
2. Add all scoped rows; record failures against unchanged production.
3. Implement shared classification, update all four consumers and add failure
   snapshots. No change to audio routing or call authorization.
4. Run new rows and complete Python suite once; shell syntax/Python compile
   once; rebuild/verify the native package once. Add targeted assertion-level
   mutations for gateway acceptance, direction mapping, defaults and unknown
   call handling. Count the full baseline as process-stability pass one, then run the existing
   182-case process lane nine more times on this source. Static checks, pure
   cases and Rust are not repeated ten times. Keep previous evidence historical.
5. Reconcile exact counts, canonical inventory, coverage/branch maps and handoff
   records; commit the scoped fix and evidence. Live validation remains pending
   a separately approved call; do not relabel the previous failed probe.

Risks: accepting stream classes too broadly could treat music as telephony;
exact profile gating and foreign-device tests prevent this. Stream defaults
could be misreported; explicit physical-class checks prevent that. Late state
reads cannot reconstruct past timing; documentation preserves this limit.
Rollback: revert the scoped fix commit; no persistent host or phone changes.

## State

Analysis and plan committed first (c199b36). All 218 planned rows are implemented
in test_hfp_node_classification.py: Positive 37, N2 30, N3 1, N6 115, N7 6,
N9 29. N1 type boundaries use N6 as external properties; N4/N5/N10/N12 retain
existing coverage plus ownership/privacy/cleanup assertions in the new rows.
N8 and N11 are not applicable to this change (no time formats or billing).

Before implementation, 218 rows ran in 73.883 seconds: 66 assertion failures
and 132 missing-helper errors. The first implementation run exposed eight
fixture-default mismatches: the harness uses sink 41/source 42, while these
fixtures use source 41/sink 42. Tests now inject explicit matching default IDs;
assertions are preserved, including rejection of streams as default devices.
The initial failure count includes fixture failures and must not be treated as
66 confirmed production defects. All eight targeted mutations were killed by
assertion failures, after their unchanged selections passed. The full 1665-method
Python suite, including all 218 new rows, passed in 322.559 seconds. Shell syntax
and Python compilation passed once. The native amd64 package rebuilt and passed
checksum, metadata, layout and both extracted binary checks; probes are repository
feasibility tools and are not shipped in this headless package. Rust is unchanged.
The full run supplied process-stability pass one. Nine further 182-scenario
process-only passes succeeded in 51.584–97.215 seconds: ten consecutive passes
with zero failures or observed flakes. Pure/static/Rust cases were not repeated.
No new hardware operation or call.
Owned scoped/mutation terminal sessions completed and closed (Terminal closed).

## Assertion-level mutation map

| Mutation | Required failing assertion |
| --- | --- |
| Gateway profile removed from shared recognition | exact profile recognition and direction |
| Gateway output direction inverted | downlink equals source |
| Gateway input direction inverted | uplink equals sink |
| Gateway stream counted as physical default source | default source remains false for streams |
| Gateway excluded by SCO consumer | both stream endpoints prove node readiness |
| Gateway excluded by health consumer | exact HFP error-growth count |
| Gateway excluded by watcher | exact HFP graph count |
| Failed final call read reported absent | final call state remains unknown |

Each of the eight unchanged mutation selections passed before mutation. All
eight modified selections failed by assertions, rather than syntax/import
errors. Full mutation logs remain under ignored work/. No real phone was used.

## Verification-tool follow-up — complete

Audit found that the new end-of-wait canonical-empty check duplicated the old
SCO mutation anchors. The repair plan was documented before editing tooling.
The two retained SCO anchors now include their preflight grep context; each
mutation and selected assertion is preserved. Commit 72de7a6 records this
reversible test-tool repair. Production hashes and process selection did not
change. Tool compilation passed. All six retained wire mutations and all eight
new HFP mutations were then revalidated: fourteen passing unmodified selections
and fourteen assertion-level kills, with zero invalid/surviving trials.

## Completion and handoff

All milestones are complete for the scoped automated correction. The inventory
contains all 218 planned scenarios, with every changed helper/rule and branch
mapped to explicit rows. Public methods, independent planned branches, invariants,
boundaries, applicable negative categories and inventoried interactions in the
changed scope have executable coverage. This is not an instrumented 100% branch
coverage claim or a hardware completion claim.

[Current evidence](evidence/m1-hfp-node-execution.json) binds full-suite results,
all ten process passes and fourteen mutation trials to source hashes. Production
source is 39172c9; verification-tool repair is 72de7a6. The corrected classifier
has not been exercised in another live call. Historical zero-count timing is
still unresolved; preserve the previous automatic failure and human computer
duplex confirmation separately. No new call, routing mutation, service restart,
phone payload recording or host package installation occurred. All owned
terminal/process sessions completed and closed (Terminal closed).

Rollback the implementation with 39172c9 and the tooling repair with 72de7a6;
revert the associated documentation/evidence when rolling back source. No
persistent host/phone state needs restoration. Next hardware step, if requested,
is one separately approved call with final call/transport observations and human
computer-audio confirmation; iPhone ANCS and recovery/permission UX remain open
M1 gates. Remote CI has not been executed for these unpublished commits.
