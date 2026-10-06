# Contributing to NativePair

NativePair follows a documentation-first, testable-by-design workflow.

## Branches

The long-lived branches are:

- `main`: stable/release integration.
- `dev`: active development.

Temporary branches may be used when required by a pull-request workflow, but they must be removed after integration. The repository should not accumulate stale branches.

## Change workflow

For any non-trivial feature, refactor, protocol change, or security-sensitive change:

1. Analyze the current architecture and relevant documentation.
2. Record the plan and affected invariants.
3. Update documentation or an ADR before changing behavior.
4. Implement the smallest approved scope.
5. Add or update tests at the lowest effective test level.
6. Run formatting, linting, and tests.
7. Commit atomically with a Conventional Commit message.
8. Update roadmap/status documentation when a milestone changes state.

## Architectural decisions

Create an ADR under `docs/adr/` when a change affects:

- public APIs or D-Bus contracts;
- persistent data formats;
- trust or security boundaries;
- protocol architecture;
- process boundaries;
- supported platforms;
- major dependencies with long-term coupling.

## Code quality

Production code must have:

- explicit dependencies;
- minimal global state;
- predictable side effects;
- clear module contracts;
- transport/protocol adapters separated from domain logic;
- deterministic tests where possible.

Do not hide device-specific behavior behind undocumented assumptions. If support varies, model it as a capability.

## Commit format

Use:

```text
feat: ...
fix: ...
refactor: ...
docs: ...
test: ...
chore: ...
ci: ...
```

Each commit should represent one logical change and remain independently understandable.

## Tests

NativePair prioritizes domain and protocol-contract tests over broad UI E2E coverage. See [docs/TESTING.md](docs/TESTING.md).

## Documentation language

Code, comments, commit messages, public documentation, and UI strings are written in English unless the file is explicitly a localization resource.
