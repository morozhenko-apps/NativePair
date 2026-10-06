# Roadmap

Roadmap states are factual project status, not release promises.

## M0 - Repository foundation

Status: **complete**

- [x] Choose Apache-2.0.
- [x] Establish `main` + `dev` branch model.
- [x] Create project governance and architecture documentation.
- [x] Create compileable Rust workspace.
- [x] Add baseline CI.
- [x] Verify all baseline checks are green.

## M1 - Protocol feasibility

Status: **in progress**

Target hardware should include at least:

- a modern Pixel Android device;
- an iPhone with a currently supported iOS release when hardware is available.

Experiments:

- [ ] Pair/trust through standard BlueZ workflow.
- [ ] MAP session can be created.
- [ ] MAP folders/messages can be listed.
- [ ] MAP message send behavior is characterized.
- [ ] MAP event notification behavior is characterized.
- [ ] PBAP contact listing is characterized.
- [ ] HFP call-control feasibility is characterized.
- [ ] HFP audio path is characterized.
- [ ] iPhone ANCS discovery and event flow is characterized.
- [ ] Failure cases and permission UX are documented.

Infrastructure:

- [x] Define privacy-safe phase-0 Bluetooth probe.
- [x] Establish headless Debian package build and CI installation gate.
- [ ] Record first Pixel probe evidence.
- [ ] Record capability matrix.

Deliverable: a capability matrix backed by reproducible commands/logs and no personal payloads in committed fixtures.

## M2 - Core daemon

Status: **not started**

- Device model and capability state machine.
- BlueZ discovery adapter.
- Versioned D-Bus service.
- Deterministic connection lifecycle tests.
- Structured, privacy-safe diagnostics.

## M3 - Messages and contacts

Status: **not started**

- MAP read/list/send where verified.
- MAP event handling where verified.
- PBAP contacts.
- Capability-aware UI/CLI behavior.

## M4 - Calls

Status: **not started**

- Incoming/outgoing call state.
- Call control.
- PipeWire/WirePlumber audio routing.
- Permission and failure UX.

## M5 - Notifications

Status: **not started**

- iPhone ANCS notifications.
- Privacy controls.
- No claim of equivalent Android notification support without a native OS mechanism or a separately approved companion-app decision.

## M6 - Desktop product and packaging

Status: **not started**

- GTK4 UI.
- Tray/background lifecycle integration.
- Debian/Ubuntu `.deb` release packaging.
- AppImage considered after Debian packaging.
- Release CI and signed artifacts.

A headless Debian packaging baseline is intentionally established during M1 so packaging failures do not accumulate until the UI milestone.

## M7 - Optional file-transfer integration

Status: **not started**

Evaluate integration with the maintained rQuickShare fork through a narrow service boundary. This milestone does not imply a repository merge.
