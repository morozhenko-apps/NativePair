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

1. **Preparation — inspected; blocked on target confirmation.** Inspect available ADB/BlueZ devices without
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
SM-G991B HFP support can be drawn from this state. Recommended continuation:
confirm the connected SM-G991B as the intended test phone, enable Bluetooth
through its normal user interface, then correlate the device and repeat the
preflight. Alternatively reconnect the previously tested Pixel 6a. The former
uses currently available hardware but starts a separate model evidence record;
the latter continues comparable Pixel evidence but requires that phone.

Live proof is not authorized in this continuation. Once preparation is ready,
obtain fresh call authorization and a dedicated destination before stage 2.
No sensitive identifiers or payloads belong in committed evidence.
