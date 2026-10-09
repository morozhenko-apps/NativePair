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

All applicable cells below are covered by the scoped contracts. Whole-suite
status is recorded separately; inapplicable cells retain their rationale.

| Artifact | Positive | N1 | N2 | N3 | N4 | N5 | N6 | N7 | N8 | N9 | N10 | N11 | N12 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| target | Covered: valid | Covered: invalid | Covered: length | x pure | x pure | x pure | Covered: types | Covered: strict address | x no locale/time | x pure | Covered: no echo | x no billing | x no storage |
| snapshot | Covered: links | x target helper | Covered: uint32/counts | x pure | Covered: duplicates | Covered: stale defaults | Covered: corrupt graph | Covered: exact target | x no locale/time | x pure | Covered: allowlist | x no billing | x no storage |
| sample | Covered: actual snapshot | x no public input parsing | x inherited IDs | Covered: read failure | x read-only | Covered: vanished defaults | Covered: bad JSON | x inherited target | x no time decisions | x main handles interrupt | Covered: captured output | x no billing | x no writes |
| main | Covered: success/help | Covered: arguments | x no limits introduced | Covered: sample failure | x no mutation | x one-shot | x sample handles decode | Covered: missing tool/target | x no locale/time | Covered: interrupt | Covered: generic errors | x no billing | x no writes |

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
target/tool/result/interrupt/exit branches. These branches are now covered by the
scoped contracts; full-suite status is separate. Existing unrelated production
files retain their documented evidence.

Mutation assertions must kill foreign target inclusion, downlink-as-uplink,
inactive/reversed/dangling links, duplicate inflation, default substitution,
non-ALSA classification, malformed IDs, private state leakage and failure success.

## Progress

- Analysis, inventory, branch map, negative matrix and plan: complete.
- Implementation and scoped execution: complete (203 uplink + one runner case).
- Mutation review: complete (13 assertion kills with passing baselines).
- Full-suite execution: complete, 1869 methods passed in 277.339 seconds.
- Idle hardware snapshot: complete, selected Pixel correlated and four probes passed.
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

## Next live-check protocol (not yet authorized)

After green automated verification and a fresh ready-state preflight, request
one call to the previously provided private test destination and readiness of
both participants. Reconfirm the Pixel/paired-target correlation; preserve the
existing no-call/RejectSCO guards, answer limits and owned HangupAll cleanup.
Never print or persist the destination or target address. No automatic retry.

At the existing 20-second human-window marker, take passive uplink and selected
input-port snapshots while the call is active. The user may manually mute the
Ubuntu input briefly and then unmute it during that window, with the remote
participant reporting whether their voice disappeared and returned. Ask for
readiness for that explicit check before dialing; do not treat covered microphone
openings as an isolation test. The observer can report source mute changes but
does not perform them. Do not automate mute/default/link changes or create
recording streams. The call still ends through the unchanged owned cleanup.

Keep three evidence levels separate: active call/SCO, direct target uplink graph
and contemporaneous selected input/mute, and the remote participant's physical
source confirmation. If a direct link is absent, report that limitation rather
than assuming no filtered audio route. If a user input check is inconclusive,
leave physical uplink proof open and retain the observations. After the attempt,
confirm empty calls, idle transport and no orphan HFP endpoints read-only.

## Final preparation state and handoff

Implementation source: 051cc07; mutation execution correction: f2186df. All
1869 Python methods passed in 277.339 seconds, with 204 new methods counted
above. Rust fmt/Clippy/eight methods, shell syntax and observer compilation pass.
All 13 mutation baselines pass and all edits fail by assertions. The 22 previous
production hashes, 182 stability IDs and their test/harness files are unchanged;
the prior ten-pass zero-observed-flake evidence remains applicable to that lane.
No ten-run claim is made for the new pure observer; static checks run once.
All scoped public functions, decision branches, rules, boundaries, applicable
negative categories and listed interactions have explicit contracts. This is
contract coverage, not a measured 100% line/arc percentage.

Exactly one authorized Pixel 6a is available; Bluetooth is enabled and its local
address matches exactly one paired BlueZ target entirely in memory. Transport,
no-dial SCO, routing and new uplink probes all exit zero without stderr. There
is no existing call, transport is idle and RejectSCO is false. Idle codec ID 2
is not live codec proof. No HFP or orphan nodes exist while idle. The default
input is ALSA, unmuted and suspended without an audio stream; no direct uplink
is expected before a call. No call, capture, mute/default/link change, service
restart or unrelated device operation occurred. All owned sessions closed.

Evidence: [execution](evidence/m1-hfp-uplink-execution.json),
[canonical inventory](evidence/m1-automated-test-inventory.json),
[idle readiness](evidence/m1-hfp-uplink-preflight.txt). Remote CI is not run for
these local commits. Native package payload is unchanged and excludes probes.
The bounded automated/preparation task is complete; physical microphone proof
remains pending. Next action: obtain one fresh guarded-call approval and both
participants' readiness for the manual Ubuntu mute/unmute check described above.
Do not dial from a generic continuation or reuse a consumed single-call approval.
