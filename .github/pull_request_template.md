## Summary

Describe the change and the user/system behavior it affects.

## Why

Explain the problem, invariant, or architectural reason for the change.

## Validation

- [ ] Documentation/ADR updated when required
- [ ] `cargo fmt --all -- --check`
- [ ] `cargo clippy --workspace --all-targets --all-features -- -D warnings`
- [ ] `cargo test --workspace --all-features`
- [ ] No sensitive phone/user data added to logs, fixtures, or screenshots

## Risk and rollback

Describe material risks and the simplest rollback point.
