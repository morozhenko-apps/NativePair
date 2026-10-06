# Architecture

## Status

Initial architecture, accepted for the foundation phase.

## Goals

NativePair integrates Linux with Android and iPhone through capabilities already exposed by the phone OS. The architecture must support different capability sets without treating one platform as a degraded version of the other.

## Process model

NativePair uses a headless background daemon with thin clients.

```text
                     +------------------+
                     | nativepair-ui    |
                     +--------+---------+
                              |
                             D-Bus
                              |
+-------------+      +--------v---------+      +-------------------+
| Phone       |<---->| nativepair-daemon|<---->| Local persistence |
| Android/iOS |      +--------+---------+      +-------------------+
+-------------+               |
                              |
                 +------------+-------------+
                 |                          |
          BlueZ / obexd             PipeWire/WirePlumber
          MAP / PBAP / BLE                HFP audio
```

The CLI is another thin client over the same daemon contract.

## Layers

### Domain

The domain layer owns platform-neutral concepts:

- device identity;
- discovered capabilities;
- messages;
- contacts;
- calls;
- notification metadata;
- connection state.

The domain layer must not depend on BlueZ, GTK, D-Bus implementations, or filesystem details.

### Protocol adapters

Protocol adapters translate system-service APIs into domain contracts.

Planned adapters include:

- BlueZ device/discovery adapter;
- OBEX MAP adapter;
- OBEX PBAP adapter;
- HFP call-control/audio integration;
- ANCS adapter for iPhone notification support.

Adapters are replaceable and mockable by contract.

### Daemon

The daemon:

- owns connection lifecycle and reconnection;
- owns protocol sessions;
- performs capability discovery;
- exposes a versioned D-Bus API;
- emits state-change signals;
- owns local persistence where required;
- enforces logging/privacy policy.

### GUI and CLI

Clients consume the daemon API. They must not open independent Bluetooth sessions.

The GUI technology target is GTK4 with Rust bindings. GUI implementation is intentionally deferred until protocol feasibility is established.

## Capability model

Support is discovered, not hard-coded by platform.

A capability has an availability state such as:

- unknown;
- unavailable;
- available;
- temporarily unavailable.

A device being Android or iPhone may guide probing order, but it must not be treated as proof that a profile works.

## Failure model

Bluetooth and phone integrations are stateful and failure-prone. The architecture must explicitly represent:

- device disappears;
- permission revoked;
- pairing removed;
- profile advertised but operation rejected;
- session established but data unavailable;
- daemon/service restart;
- transient BlueZ/OBEX failure.

Retries must be bounded and event-driven where possible. Arbitrary sleeps are not a recovery strategy.

## Persistence

No sensitive content is persisted merely for convenience. Any future local cache of messages, contacts, calls, or notifications requires a dedicated ADR covering:

- purpose;
- retention;
- encryption;
- deletion;
- schema migration;
- privacy impact.

## Future Quick Share integration

NativePair and rQuickShare remain independent initially.

A future integration should happen only through a narrow boundary, for example a file-transfer capability interface or D-Bus service. Copying the entire Quick Share implementation into the daemon is explicitly out of scope until the protocol and product boundaries justify it.
