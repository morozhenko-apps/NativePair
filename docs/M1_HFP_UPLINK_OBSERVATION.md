# M1 passive HFP uplink observation

Date: 2026-10-10. Mode B. Branch: dev.

## Analysis and bounded scope

The existing watcher measures local playback links, not microphone-to-phone
links. Two HFP endpoints and an after-call default input do not establish the
live uplink. Add an independent, one-shot read-only diagnostic; preserve all
existing watcher output, call guards, product contracts and audio settings.
It uses the existing strict node decoder, HFP direction classifier, captured
command adapter and wpctl parsers. No dependency or routing architecture changes.

The target address is supplied only through NATIVEPAIR_DEVICE and kept in memory.
Only direct active links from Audio/Source nodes to the exact target's HFP sink
prove a direct graph connection. Count distinct sources, not channel links.
An absent direct link does not disprove filtered/loopback paths. A graph link
does not prove audible signal, physical microphone identity or active SCO.
The default input ID and mute query are separate reads after pw-dump, so this
is a best-effort observation, not an atomic graph transaction.

References: PipeWire [pw-dump](https://docs.pipewire.org/page_man_pw-dump_1.html),
[graph overview](https://docs.pipewire.org/page_overview.html).

## Plan, risks and rollback

1. Complete changed-artifact inventory, branch and interaction matrices below;
   commit this plan before implementation.
2. Add scripts/probe_hfp_uplink.py with a pure snapshot, bounded sample adapter
   and CLI. Test real classification; fake only external commands/environment.
3. Run scoped contracts and assertion-level mutations, then the full suite once,
   Rust quality gate and syntax. Keep static/pure checks out of repeated runs.
   Existing ten-pass process stability evidence is retained because no process,
   signal, FIFO or call ownership code changes; the new observer starts no
   background process and delegates bounded reads to the tested command adapter.
4. Run an idle passive snapshot on the privately correlated Pixel only. Record
   sanitized output, evidence hashes and complete handoff. Request a new guarded
   call only after preparation is concrete, with contemporaneous input-port and
   uplink observations plus human confirmation. No new call is authorized yet.

Risks: stale defaults, vanished nodes, malformed dumps, other paired devices,
duplicate channels and mistaking graph presence for voice proof. Mitigate with
exact target/direction, strict IDs, deduplication, anonymous enums and explicit
unknowns. No raw graph/identifier/voice persistence. Rollback: revert additive
observer, tests and documentation commits; existing call probes are untouched.

## Complete changed-artifact inventory and branch map

Existing production inventory remains in M1_AUTOMATED_VERIFICATION.md. This
bounded addition has three public functions and one private validation helper.

| Artifact | Risk / level / rationale | Branches and planned tests |
| --- | --- | --- |
| _valid_target | High / unit / exclude invalid or private text | ASCII address, lowercase, uppercase; missing/null/non-string/short/long/malformed/unicode; no echo |
| snapshot | High / unit / no false microphone proof | Invalid target or graph root -> None; strict valid_nodes inherited; missing/stale/invalid default -> unknown; exact target case-insensitive; each HFP profile x each media class; source versus sink; active/inactive/unknown link; malformed info/type/endpoint IDs; wrong/reversed/dangling/self links; duplicate channels/sources/endpoints; default/nondefault ALSA/Bluetooth/virtual sources; allowlisted source states |
| sample | High / contract / bounded captured reads only | Missing/invalid/root-invalid dump -> None; valid graph -> actual snapshot; default read failed/stale/valid; source mute yes/no/unknown; no raw output escapes |
| main | High / contract / privacy and read-only CLI | Help, unknown argument, invalid/missing target, each missing tool, failed sample, success, interrupted sample; exact stdout enums and exit codes; no command for invalid input |

No subject under test is mocked. sample/main use fake external command adapters;
shared pure decoders and snapshot execute unchanged. Inventory is complete
before test implementation. Planned count: 100+ separately registered rows;
reconcile exact categories and scenarios with the executable inventory.

## Negative matrix

Every applicable cell is planned until execution is recorded below.

| Artifact | Positive | N1 | N2 | N3 | N4 | N5 | N6 | N7 | N8 | N9 | N10 | N11 | N12 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| target | ? valid | ? invalid | ? length | x pure | x pure | x pure | ? types | ? strict address | x no locale/time | x pure | ? no echo | x no billing | x no storage |
| snapshot | ? links | x target helper | ? uint32/counts | x pure | ? duplicates | ? stale defaults | ? corrupt graph | ? exact target | x no locale/time | x pure | ? allowlist | x no billing | x no storage |
| sample | ? actual snapshot | x no public input parsing | x inherited IDs | ? read failure | x read-only | ? vanished defaults | ? bad JSON | x inherited target | x no time decisions | x main handles interrupt | ? captured output | x no billing | x no writes |
| main | ? success/help | ? arguments | x no limits introduced | ? sample failure | x no mutation | x one-shot | x sample handles decode | ? missing tool/target | x no locale/time | ? interrupt | ? generic errors | x no billing | x no writes |

## Interaction, coverage and mutation plan

- Both profiles x Audio/Source, Audio/Sink, Stream/Output/Audio,
  Stream/Input/Audio, unknown class; exact and foreign addresses.
- Default/nondefault source x ALSA/BlueZ/virtual API; active/inactive link;
  repeated channels versus multiple distinct sources; missing/stale defaults.
- Source states running/idle/suspended/error/unknown/private text;
  endpoint IDs 0/1/max-1/max and invalid type/range; malformed objects/info.
- Failed dump/default/mute commands x parse outcome; CLI short-circuits invalid
  input and tool loss; interrupt never retries or changes audio.

Coverage map: target helper — validation branches; snapshot — node/target/source/
link/state branches; sample — dump/decode/default/mute branches; main — argument/
target/tool/result/interrupt/exit branches. All are planned, none claimed covered
yet. Existing unrelated production files retain their documented evidence.

Mutation assertions must kill foreign target inclusion, downlink-as-uplink,
inactive/reversed/dangling links, duplicate inflation, default substitution,
non-ALSA classification, malformed IDs, private state leakage and failure success.

## Progress

- Analysis, inventory, branch map, negative matrix and plan: complete.
- Implementation, execution, mutation review and idle hardware snapshot: pending.
- Live microphone proof: pending fresh single-call approval and human check.

### Mutation runner correction discovered during execution

Five initial trials unexpectedly survived although their assertions directly
contradict the edits. The disposable mutation runner can reuse Python bytecode
when baseline and mutated source have equal size and the same coarse timestamp.
This makes mutation evidence unreliable. Before accepting any new mutation
result, run Python mutation subprocesses with -B in the fresh disposable tree
(which already excludes __pycache__). Add one N6 regression: a same-length
source edit with identical mtime must fail the real assertion after a successful
baseline; assert no bytecode is written. This covers execute's changed Python
invocation branch. Rust execution and all product code remain unchanged.
The initial mutation output is provisional and will be replaced, not counted.

### Implementation and scoped verification complete

The additive observer and 203 direct-uplink scenarios are implemented; the
mutation runner correction adds one regression (204 new methods total).
The scoped contracts pass. All 12 uplink mutation baselines pass and their edits
are killed by assertion failures after disabling bytecode writes. A thirteenth
trial removes that protection and is killed by the new same-size/mtime regression.
The initial stale-bytecode results are superseded, not included as passing trials.

Exact primary counts: Positive 36; N1 22; N2 8; N3 6; N4 5; N5 10;
N6 86; N7 29; N9 1; N10 1. N8 is inapplicable (no calendar/locale decisions),
N11 has no billing/entitlements, N12 has no storage writes. Privacy and exact
state assertions apply across other rows without double-counting their category.
The inventory estimate was exceeded because malformed endpoint types and
profile/class/target combinations each receive independent registered rows.

All applicable planned matrix cells and coverage-map branches are now covered
by explicit scoped contracts; full-suite execution and idle hardware readiness
remain pending. The only production addition is the standalone observer;
existing call, routing, watcher, decoder and command-adapter behavior is unchanged.
