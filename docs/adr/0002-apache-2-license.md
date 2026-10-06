# ADR-0002: Apache License 2.0

- Status: Accepted
- Date: 2026-10-06

## Context

NativePair is intended to be open source and reusable. The project should require preservation of attribution while allowing broad reuse, including commercial reuse. A future integration with GPLv3-licensed rQuickShare code is possible.

## Decision

License NativePair under Apache License 2.0.

Maintain:

- `LICENSE` with the full Apache-2.0 license text;
- `NOTICE` for project and third-party attribution notices.

## Rationale

Apache-2.0 provides permissive reuse, explicit attribution requirements, and an explicit patent license. Apache-2.0 code can be incorporated into a GPLv3 combined work if a future integration requires it.

## Consequences

Downstream users may create proprietary derivative products provided they comply with Apache-2.0 requirements. NativePair does not impose GPL-style copyleft on independent downstream derivatives.

If GPLv3 code is incorporated directly into NativePair in the future, licensing of the combined work must be reviewed before that integration is merged.
