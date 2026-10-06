# ADR-0001: Headless Rust daemon with capability-oriented adapters

- Status: Accepted
- Date: 2026-10-06

## Context

NativePair must integrate with stateful Linux system services, continue operating when the UI is closed, support Android and iPhone without forcing feature parity, and remain testable without physical hardware for most logic.

## Decision

Use Rust for the core implementation.

Use a separate headless daemon as the owner of Bluetooth/protocol sessions. Expose application functionality to thin clients through D-Bus.

Use capability-oriented protocol adapters rather than platform-specific application cores.

Initial technology direction:

- Rust;
- Tokio for asynchronous orchestration where needed;
- zbus for D-Bus;
- BlueZ and obexd for Bluetooth/OBEX integration;
- PipeWire/WirePlumber integration for call audio where required;
- GTK4 with gtk-rs for the future desktop GUI.

## Consequences

Positive:

- background state is independent from GUI lifecycle;
- domain logic can be tested without BlueZ;
- Android and iPhone can expose different capability sets cleanly;
- a future CLI or desktop integration can reuse the same daemon API.

Costs:

- process boundaries and D-Bus contracts add design work;
- BlueZ/OBEX behavior must be modeled explicitly;
- GTK implementation is separate from protocol work.

## Guardrail

The project must not build user-facing features around a phone capability until that capability has been verified on representative hardware.
