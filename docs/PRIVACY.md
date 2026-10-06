# Privacy Model

NativePair is designed for local device integration.

## Baseline invariants

- No NativePair cloud account is required.
- Baseline communication is local between the Linux host, Linux system services, and the paired phone.
- The project does not operate a server that receives message, contact, call, or notification content.
- Personal payloads are excluded from normal logs.
- Telemetry is absent unless a future explicit product decision introduces it.

## Sensitive data

Treat these as sensitive by default:

- message content and metadata;
- contacts;
- phone numbers;
- call history and call state;
- notification contents;
- stable device identifiers;
- device names when they can identify a person;
- Bluetooth addresses.

## Diagnostics

Diagnostics should prefer:

- capability names;
- protocol/state transitions;
- generic error categories;
- ephemeral correlation IDs.

If a stable identifier is required for troubleshooting, it must be redacted or transformed before logs leave the local machine.

## Future persistence

Persisting sensitive phone data is not part of the foundation phase. Any persistence feature requires a privacy/security ADR before implementation.
