# M1 HFP audio continuation

Date: 2026-10-09. Mode: B — hardware verification. Branch: dev.

## Analysis and scope

The automated source contracts are complete locally. M1 remains open because
the previous audible conversation did not establish which physical speaker
and microphone carried the call. The existing guarded SCO probe now refreshes
call objects and observes transport state before activation. Reuse this probe;
do not introduce a routing architecture or new product API during diagnostics.

The user's request to continue permits preparation and reversible transport
preflight. FEASIBILITY.md requires fresh explicit approval for another live
call. No call, SMS, service restart, audio stream, default-route change or
PipeWire link mutation is included in the preparation stage.

## Plan and milestones

1. **Preparation — complete for Pixel; live proof awaiting authorization.** Inspect available ADB/BlueZ devices without
   printing addresses, serials or names. Select the existing configured target
   or a unique paired HFP phone; ambiguity requires a user decision. Run the
   existing transport and no-dial SCO preflights and read-only routing snapshot.
   Record current call absence/presence, transport state, RejectSCO, codec and
   endpoint/default-routing evidence. Missing services/devices or blocked
   transport remain explicit unknown/blocker results.
2. **Live proof — computer duplex human-confirmed; endpoint enumeration unresolved.** Present the actual
   preflight results before requesting a dedicated destination and human
   readiness. One guarded Dial attempt only; never touch a pre-existing call.
   Wait for the remote answer and active call, observe/activate the transport
   through existing logic, inspect matching source/sink endpoints and use the
   existing bounded human verification window. Existing cleanup hangs up the
   owned call on success, failure or interruption. Do not change routing.
3. **Evidence and handoff — complete for this attempt.** Record anonymous system results and
   explicit human confirmation of the computer output and microphone. Do not
   classify phone-to-phone audibility as Linux duplex proof. If manual routing
   is required, stop and present architecture/UX options before implementing it.

## Inventory, branches and acceptance

This is a manual hardware continuation of the existing M1 inventory, not a new
automated suite. Automated branch, negative, interaction and mutation evidence
is in M1_AUTOMATED_VERIFICATION.md and M1_COVERAGE_MAP.md.

- Preparation: missing/unauthorized/ambiguous device; unpaired/unavailable HFP;
  missing manager/transport; unreadable properties; existing call; RejectSCO;
  idle/pending/active transport; absent/default/non-default matching endpoints.
- Live proof: existing-call refusal; one attempted Dial; answer timeout; fresh
  call-object state; automatic active/pending/idle transport; failed activation
  with state readback; distinct source/sink readiness; owned-call cleanup.
- Human evidence: downlink through the identified computer output and uplink
  through the identified computer microphone. Both must be confirmed separately.

## Risks, rollback and implementation changes

HFP connection may change Bluetooth profile state. No global audio defaults,
links or host services are modified. Do not disconnect an existing user-owned
connection as an automatic rollback. Live calls can interrupt the user and
incur charges, hence fresh authorization and a dedicated test recipient are
required before stage 2. No production code, architecture or dependencies are
planned. Documentation commits can be reverted independently; existing probes
own their temporary files and terminate their owned call during cleanup.

## Initial preparation state (historical)

The plan was committed before hardware operations (b564d13). Preparation ran
the existing audio transport probe, no-dial SCO probe and read-only routing
snapshot. All owned process/terminal sessions completed and closed (Terminal
closed). No call, Activate invocation, audio stream, link/default change or
service restart was performed.

- ADB has one authorized device: model SM-G991B, Android 15. The prior hardware
  evidence was for a Pixel 6a. The intended device for this continuation must
  therefore be confirmed by the user before further Bluetooth operations.
- Android reports bluetooth_on=0, enabled=false and state=BLE_ON. Bluetooth
  Classic is not currently enabled on the ADB-connected phone.
- BlueZ reports one paired device advertising HFP AG. The preparation selected
  this unique candidate, but its identity has not been correlated with the
  ADB-connected phone; do not infer that this is the same physical device.
- Host Bluetooth, PipeWire and WirePlumber are active. HFP audio preflight
  ended with a connect timeout; no-dial SCO preflight could not establish a
  gateway. The Telephony manager is readable but enumerates zero gateways.
- Read-only routing shows zero HFP nodes, available default sink/source
  snapshots, no phone HFP defaults and no orphan HFP nodes. The current call
  state is unknown because no gateway is available, not a proven empty call set.

Sanitized preparation evidence is in
[the preparation log](evidence/m1-hfp-audio-preparation.txt). No conclusion about
SM-G991B HFP support can be drawn from this state.

The user subsequently selected the previously tested Pixel 6a. A fresh ADB
inventory now contains two authorized phones, including exactly one Pixel 6a
and one SM-G991B. Select the Pixel by its verified model rather than using the
implicit default ADB target. Read its Bluetooth state and correlate its local
adapter address with a paired BlueZ target entirely in memory before any HFP
connection attempt. Do not print/store either device's serial, address or name.
The SM-G991B is outside the selected continuation scope. If correlation is
unavailable or ambiguous, stop before connecting.

Reversible preparation detail: the selected Pixel reports Bluetooth disabled.
Its local `svc bluetooth` help documents the ordinary enable/disable operation,
whereas `cmd bluetooth_manager help` is not supported on this build. Use one
`svc bluetooth enable` attempt as normal radio setup for the user-selected HFP
verification, then condition-observe enabled state and correlate the local
address before connecting. This does not alter pairing permissions or product
architecture. Record the initial disabled state. If the ordinary operation is
rejected or identity remains unknown, stop and request manual settings/device
confirmation. Do not force privilege changes or restart services. Keep the
radio available for this selected verification stage; do not automatically
disable it if that could interrupt a user-owned connection.

At this preparation stage, live proof was not yet authorized. Once ready,
obtain fresh call authorization and a dedicated destination before stage 2.
No sensitive identifiers or payloads belong in committed evidence.

## Selected Pixel preparation result

The user confirmed the Pixel 6a and enabled Bluetooth. Its local Bluetooth
address matches the existing paired BlueZ device; only this correlated target
was used for subsequent preflights. Model Pixel 6a, Android 17. A normal radio
enable operation returned success during setup; radio is left enabled for the
selected test stage. No unrelated device settings or pairing were changed.

HFP audio preflight succeeds. A real wire-signature mismatch initially blocked
the no-dial SCO guard; the [GetCalls correction](M1_GETCALLS_COMPATIBILITY.md)
adds 84 regressions and passes the complete suite. After that fix, no-dial SCO
and passive HFP both confirm an empty call set. Transport is idle, RejectSCO
is false and Activate is available. Read-only routing confirms no HFP nodes,
no phone HFP default routes and no orphan nodes. No live call or audio stream
has been created. These results establish preflight readiness, not Linux
duplex audio support.

[Pixel evidence](evidence/m1-pixel-hfp-preflight.txt) contains bounded status
fields only. The dedicated destination is not configured. Await explicit
authorization for one guarded outgoing test call and the destination; require
human confirmation of computer output and microphone during the existing
20-second check window. Existing guard, time limits and owned-call HangupAll
cleanup remain unchanged. No routing architecture change is authorized.

## Authorized live attempt

The user supplied a dedicated destination in direct response to the explicit
single-call authorization question. This authorizes one guarded outgoing SCO
test to that destination. Keep the number only in the process environment;
never put it in repository files, evidence or normal diagnostics. Do not
automatically retry Dial. Reconfirm the Pixel identity/BlueZ correlation in
memory and let the existing probe enforce an empty call set and RejectSCO=false
immediately before its one Dial attempt. Use the documented defaults: up to
30 seconds for the remote answer, 15 seconds for SCO/node readiness and a
20-second human check window. Preserve all existing owned-call cleanup.

After completion, inspect call absence, idle transport and orphan endpoints
read-only; record sanitized status and ask which physical output/microphone
carried the audio. Successful transport/endpoints alone do not complete duplex
proof. No production changes, manual routing or service restarts are planned.
The already successful regression suite is not repeated for this hardware run.

## Authorized live result (2026-10-09)

One guarded attempt ran at 22:26:54–22:27:30 UTC on the correlated Pixel 6a.
The probe confirmed no pre-existing call, attempted Dial once, received a
successful reply and observed the call reaching active. Transport was already
active before the activation decision; Activate was therefore never invoked.
The existing endpoint classifier reported zero matching HFP nodes and neither
source nor sink. The probe exited with hfp_nodes_not_ready before its human
verification window, and the owned-call HangupAll cleanup succeeded.

Read-only post-call verification confirms a successful GetCalls query with an
empty set, transport idle, no HFP/default phone routes and no orphan HFP nodes.
No routing/default/link changes or host service restart were performed. All
owned command/process sessions completed and closed (Terminal closed).

The user reports voice and sound working normally in both directions and then
explicitly confirms that both the output and microphone were on the computer.
This establishes human-confirmed computer duplex audio on this Pixel/host
combination, supported by the observed active SCO transport. Do not weaken the
distinct-source/sink assertion or infer that hardware audio failed merely
because the current classifier found no matching nodes. No contemporaneous
unfiltered graph was retained, so the zero count cannot distinguish missing
endpoints from a filtering/representation mismatch after the call has ended.

Sanitized evidence: [live attempt](evidence/m1-pixel-sco-live-attempt.txt) and
[post-call state](evidence/m1-pixel-sco-post-call.txt). No destination number or
voice payload is stored. The authorization was consumed by this one Dial
attempt; no automatic repeat is authorized. HFP audio feasibility is now
characterized by one human-confirmed computer duplex call. Automated endpoint
enumeration remains unresolved; the probe result is still a failure and must
not be relabelled successful. A scoped privacy-safe graph diagnostic can be
planned before another separately approved live test. This is not a claim of
repeatability, recovery, all-device support or product routing readiness.

## Endpoint classifier follow-up

The zero count is not evidence that the counter never ran: endpoint snapshots
were attempted during the bounded wait, before the probe's own HangupAll. A
remote/manual early hangup could remove nodes during that wait; the retained
log does not record the final call/transport state and cannot establish timing.
A separate source-confirmed defect excluded headset-audio-gateway and its
stream classes. The [scoped correction](M1_HFP_NODE_CLASSIFICATION.md) recognizes
these nodes in all audio diagnostics and records anonymous final call/transport
state on failure before cleanup. Automated verification is separate from live
validation. The original failed result is preserved; the existing one-call
authorization is consumed.

## Corrected-classifier hardware revalidation plan

Continuation after 864ae87. Mode B. The user requests continuation; preparation
is authorized, but the previous single-call authorization is consumed.

1. Reconfirm exactly one authorized Pixel 6a through ADB model queries and
   correlate its local Bluetooth address with a paired BlueZ target in memory.
   Do not print/store serials, addresses, device names or destinations. Observe
   radio state; if unavailable/ambiguous, stop before transport operations.
2. Run existing transport, no-dial SCO and read-only routing probes against
   only the correlated Pixel. Record bounded status fields and call absence,
   RejectSCO, transport state and endpoints. No Dial, HangupAll, Activate,
   default/link changes, audio streams, service restarts or message operations.
3. Once ready, request fresh explicit approval for one outgoing guarded call
   to the same previously provided test destination, plus human readiness.
   Keep the destination in memory/environment only. Do not dial until approval.
4. For an approved attempt only, reconfirm identity and use existing guards,
   answer/readiness limits and owned cleanup. Ask the human to leave the call
   connected until automatic completion and verify both computer audio paths.
   Preserve any failed endpoint result and new final call/transport fields.
5. Inspect post-call absence, idle transport and remaining endpoints read-only;
   record sanitized evidence and human confirmation, update capability/roadmap
   wording only to the established evidence level, and commit the handoff.

The existing automated gate is complete and unchanged; do not repeat static,
pure or process stability tests for a hardware-only continuation. No code,
architecture, dependencies or routing change is planned. Risks remain early
remote/manual hangup, service/device loss and unknown reads. A pre-existing call
must remain untouched. Rollback is owned-call cleanup only after approved Dial;
never disconnect user-owned connections or restore global settings automatically.

State: plan recorded before hardware preparation. Matrix progress wording in
the classifier record is reconciled with the completed 218-row execution;
no tests or production behavior changed.

### Initial revalidation preparation result (historical: device missing)

The revalidation plan was committed first (f01bb41). ADB inventory succeeds but
contains zero devices: no authorized, unauthorized or offline entries. Exactly
zero authorized Pixel 6a devices are available, so identity correlation and all
transport/SCO/routing preflights were not attempted. No Bluetooth connection,
call, Activate, HangupAll, audio stream, routing/default/link change or service
restart occurred. The selected target remains Pixel 6a; do not substitute an
unrelated phone automatically. No automated test rerun is needed for this
hardware-availability blocker. Owned command sessions ended (Terminal closed).

[Sanitized preparation evidence](evidence/m1-hfp-revalidation-preflight.txt).
Resume stage 1 after the user connects Pixel 6a over USB and authorizes ADB if
prompted. Repeat identity correlation and the no-call preflights before asking
for the separate one-call approval. The previously supplied destination must
remain private and must not be used without fresh live-call authorization.

### Corrected-classifier preflight ready (2026-10-10, Europe/Lisbon)

The user connected the selected phone. Exactly one authorized Pixel 6a is now
available over ADB; Android release 17, Bluetooth enabled. Its local Bluetooth
address matches exactly one paired BlueZ device, correlated only in memory.
The existing transport, no-dial SCO and read-only routing probes all exit zero.
PipeWire/WirePlumber are active, HFP session and transport API are available,
GetCalls confirms no existing call, State is idle and RejectSCO is false.
The idle transport reports codec ID 2 (mSBC); this is not live codec/audio proof.
No HFP nodes, phone HFP defaults or orphan HFP nodes are observed while idle.

[Ready-state evidence](evidence/m1-hfp-revalidation-ready.txt) contains bounded
fields only. No destination, serial, address or device name is persisted. No
Dial, HangupAll, Activate, audio stream, default/link change or service restart
occurred. Owned command sessions completed and closed (Terminal closed).

Stage 1 and stage 2 preparation are complete; stage 3 awaits fresh explicit
approval for one outgoing call to the previously supplied private destination.
The user's readiness reply authorized USB preparation, not another telephone
call. Ask whether both participants are ready to answer and check computer
output/microphone, leaving the call connected until automatic probe completion.
Use the existing 30-second answer, 15-second node and 20-second human window
limits. Reconfirm identity and the no-existing-call guard immediately before
an approved attempt. No automated tests or source changes are needed here.
