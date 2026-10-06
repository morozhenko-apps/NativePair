# NativePair

NativePair is a Linux phone-integration project for Android and iPhone that aims to use capabilities already built into the phone operating system.

**No companion app is required for the baseline feature set.**

The project is currently in **pre-alpha / protocol feasibility**. The first goal is to verify what modern Android and iPhone devices expose reliably through standard Bluetooth profiles on Linux before building user-facing features around them.

## Product principles

- Use native phone capabilities before inventing a custom protocol.
- Require no Android or iPhone companion application for baseline functionality.
- Keep personal data local by default.
- Treat device capabilities as discovered facts, not assumptions based only on platform name.
- Keep the background service independent from the GUI.
- Prefer a small, focused Linux integration over a KDE Connect-style feature bundle.
- Ship a first-class Debian/Ubuntu package.

## Planned capabilities

| Capability | Android | iPhone | Linux side | Status |
| --- | --- | --- | --- | --- |
| SMS / messages | Bluetooth MAP | Bluetooth MAP | BlueZ + OBEX | Feasibility testing required |
| Contacts | PBAP | PBAP | BlueZ + OBEX | Feasibility testing required |
| Calls | HFP | HFP | BlueZ + PipeWire/WirePlumber integration | Planned |
| App notifications | No universal native equivalent identified | ANCS | BlueZ BLE | Planned for iPhone |
| File transfer | Future integration point | Future integration point | Separate transport | Out of initial scope |

Support varies by phone model, OS version, permissions, Bluetooth stack behavior, and Linux environment. A capability is not considered supported until it is verified end-to-end.

## Architecture direction

```text
Android / iPhone
       |
       | Standard Bluetooth profiles
       v
BlueZ / obexd / audio stack
       |
       v
nativepair-daemon
       |
       +---- D-Bus API ---- nativepair-ui
       |
       +---- D-Bus API ---- nativepair CLI
```

The daemon owns transport and protocol state. Domain logic is isolated from BlueZ and exposed through explicit interfaces so it can be tested without real hardware.

See [Architecture](docs/ARCHITECTURE.md) and the [ADR index](docs/DECISIONS.md).

## Initial scope

NativePair starts with protocol feasibility, not GUI work.

The first hardware spike must validate:

1. MAP session creation and message listing.
2. MAP message sending where the phone permits it.
3. MAP notification/event delivery.
4. PBAP contact listing.
5. HFP call-control feasibility.
6. iPhone ANCS notification feasibility.

Android results must include at least one modern Pixel device because profile availability alone does not guarantee compatible runtime behavior.

## Non-goals

For the initial product:

- no cloud relay;
- no mandatory account;
- no mandatory phone-side application;
- no private replacement Bluetooth stack;
- no promise of feature parity between Android and iPhone;
- no Quick Share implementation inside NativePair.

Quick Share may become an integration later, but it remains a separate subsystem and project until there is a clear architectural reason to merge them.

## Repository workflow

- `main` is the release/stable integration branch.
- `dev` is the active development branch.
- Documentation is updated before implementation when behavior or architecture changes.
- Commits use Conventional Commit prefixes such as `feat:`, `fix:`, `docs:`, `refactor:`, and `test:`.
- CI must be green before promoting `dev` to `main`.

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

NativePair is licensed under the Apache License 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
