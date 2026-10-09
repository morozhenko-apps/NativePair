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
| shared classifier | Planned | Planned via N6 types | Planned via N6 missing | NA pure | NA pure | NA pure | Planned exhaustive product | NA no identity | NA no dates | NA pure | Existing + no output | NA no billing | NA pure |
| SCO/routing | Planned | Existing | Planned | Existing | Existing one Dial | Existing | Planned | Planned | NA no dates | Existing | Planned cross-cutting | NA no billing | Existing + cleanup |
| health/watcher | Planned | Existing | Existing | Existing | NA read-only | Existing | Planned | NA no auth changes | NA no dates | Existing | Existing | NA no billing | Existing |
| end-of-wait observations | Planned active call | NA enums | Planned absent | Planned | Existing cleanup once | Planned combinations | Planned unknown | Existing guards | NA no dates | Planned early hangup | Planned cross-cutting | NA no billing | Existing cleanup |

## Milestones, risks and rollback

1. Commit this analysis, inventory, decisions and plan before tests/code.
2. Add all scoped rows; record failures against unchanged production.
3. Implement shared classification, update all four consumers and add failure
   snapshots. No change to audio routing or call authorization.
4. Run new rows and complete Python suite once; shell syntax/Python compile
   once; rebuild/verify packaged helpers once. Add targeted assertion-level
   mutations for gateway acceptance, direction mapping, defaults and unknown
   call handling. Previous ten-run process evidence remains tied to 5d72c31;
   no signal/ownership code changes require repeating static checks ten times.
5. Reconcile exact counts, canonical inventory, coverage/branch maps and handoff
   records; commit the scoped fix and evidence. Live validation remains pending
   a separately approved call; do not relabel the previous failed probe.

Risks: accepting stream classes too broadly could treat music as telephony;
exact profile gating and foreign-device tests prevent this. Stream defaults
could be misreported; explicit physical-class checks prevent that. Late state
reads cannot reconstruct past timing; documentation preserves this limit.
Rollback: revert the scoped fix commit; no persistent host or phone changes.

## State

Analysis complete. Plan and inventory recorded before implementation. No new
hardware operations or calls performed. Test and implementation stages pending.
