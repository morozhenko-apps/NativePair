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

1. **Preparation — planned.** Inspect available ADB/BlueZ devices without
   printing addresses, serials or names. Select the existing configured target
   or a unique paired HFP phone; ambiguity requires a user decision. Run the
   existing transport and no-dial SCO preflights and read-only routing snapshot.
   Record current call absence/presence, transport state, RejectSCO, codec and
   endpoint/default-routing evidence. Missing services/devices or blocked
   transport remain explicit unknown/blocker results.
2. **Live proof — awaiting separate authorization.** Present the actual
   preflight results before requesting a dedicated destination and human
   readiness. One guarded Dial attempt only; never touch a pre-existing call.
   Wait for the remote answer and active call, observe/activate the transport
   through existing logic, inspect matching source/sink endpoints and use the
   existing bounded human verification window. Existing cleanup hangs up the
   owned call on success, failure or interruption. Do not change routing.
3. **Evidence and handoff — planned.** Record anonymous system results and
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

## Current state

Plan recorded before hardware operations. Preparation has not run. Live proof
is not authorized in this continuation. No sensitive identifiers or payloads
belong in this file or committed evidence.
