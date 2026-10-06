# NativePair Agent Guide

This file is the repository-level source of truth for automated development work.

## Operating rules

1. Read relevant documentation before changing code.
2. Classify work as either feature/refactor work or testing work.
3. For significant architecture, public API, data-model, security-boundary, or material UI/UX decisions, document options and obtain an explicit decision before implementation.
4. For reversible implementation details, decide autonomously, document the rationale where useful, and keep scope narrow.
5. Update documentation before code when behavior, architecture, or invariants change.
6. Keep commits atomic and use English Conventional Commit messages.
7. Never weaken tests to match defective behavior.
8. Prefer dependency injection and explicit interfaces over global state.
9. Never log message bodies, contact data, notification contents, phone numbers, or other personal payloads in normal diagnostics.
10. Keep the repository recoverable: another engineer should be able to continue from committed code and documentation alone.

## Branch policy

- Work lands on `dev`.
- `main` is updated only from a green, reviewed `dev` state.
- Long-lived branches are limited to `main` and `dev`.

## Current project phase

The current phase is protocol feasibility and foundation work. Do not build product UI around an unverified capability.

## Required reading

- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
- `docs/TESTING.md`
- `docs/PRIVACY.md`
- `docs/DECISIONS.md`
