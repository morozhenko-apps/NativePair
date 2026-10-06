# Security Policy

NativePair handles sensitive local data such as messages, contacts, call metadata, device identifiers, and potentially notification contents. Security and privacy boundaries are part of the product contract.

## Current status

NativePair is pre-alpha. No production release is available yet.

## Reporting a vulnerability

Please use GitHub's private security reporting / Security Advisory mechanism for this repository when available. Do not publish sensitive exploit details in a public issue before a fix or mitigation is available.

## Security invariants

The project must preserve these invariants unless an explicit security ADR changes them:

- No cloud service is required for baseline operation.
- Message, contact, call, and notification content must not be transmitted to project-owned servers.
- Sensitive payload contents must not be written to normal application logs.
- Bluetooth trust must rely on the operating system pairing/trust model rather than bypassing it.
- Privileged operations must be minimized and isolated.
- The GUI must not require broader permissions than the daemon/backend actually needs.
- Protocol input is untrusted and must be parsed defensively.
- Device identity and capability state must not be inferred from display names alone.
- Diagnostics must redact personal content and stable device identifiers by default.

## Dependency policy

Security-sensitive dependencies and system-service integrations must be reviewed before introduction. CI will evolve to include dependency vulnerability scanning as the dependency graph becomes non-trivial.
