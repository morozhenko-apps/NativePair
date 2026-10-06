# Testing Strategy

## Purpose

Tests protect behavior, protocol contracts, privacy invariants, and state transitions. Coverage percentage is not a goal by itself.

## Test pyramid

Preferred distribution:

- 70-80% unit/domain;
- 15-25% integration/contract;
- 5-10% end-to-end or hardware smoke tests.

Hardware-dependent tests are not substitutes for deterministic domain and adapter tests.

## Required qualities

Tests must be:

- deterministic;
- order-independent;
- explicit about final state and side effects;
- free from arbitrary sleeps;
- based on fakes/adapters for external services;
- strong enough to fail when meaningful domain behavior is mutated.

## Priority risk areas

- capability-state transitions;
- reconnect and service restart behavior;
- malformed protocol payloads;
- permission revocation;
- duplicate/replayed events;
- concurrency between discovery/session teardown;
- stale device state;
- personal data leakage in logs;
- persistence migration if sensitive caching is ever introduced.

## Protocol fixtures

Protocol fixtures must use synthetic data. Never commit real:

- message bodies;
- phone numbers;
- contacts;
- call history;
- notification text;
- Bluetooth identifiers tied to a user's device.

## CI baseline

Every code change should eventually pass:

```bash
cargo fmt --all -- --check
cargo clippy --workspace --all-targets --all-features -- -D warnings
cargo test --workspace --all-features
```

Additional security and packaging checks will be added when relevant dependencies and release artifacts exist.

## Hardware verification

Hardware tests must document:

- device model;
- OS version;
- Linux distribution;
- BlueZ version;
- relevant permissions;
- exact capability being verified.

Logs included in issues or test evidence must be sanitized before publication.
