# GitHub Actions release-only packaging and fast branch checks

Date: 2026-10-18. Status: planned and tested only after associated CI evidence.

## Baseline
- Public NativePair repository, default main and development dev. Standard GitHub-hosted Linux is free for public repositories; do not route untrusted pull request code through the local runner.
- The current `ci.yml` runs Rust quality plus Debian packaging and install smoke on **every** dev/main branch push.
- Branch/PR concurrency already cancels superseded checks. The repository's checkout/toolchain action hashes are pinned. Keep all M1 contract tests in the fast CI; do not reduce coverage.

## Implementation
1. [complete] Inspect the current dev workflow and branch relationship.
2. [planned] On dev/main/PR run Rust quality and deterministic M1 contract tests once. Do not build/install/upload native packages on every branch push.
3. [planned] On a versioned annotated tag whose commit equals current main HEAD, run the Rust checks and the Debian package gate. Do not cancel release-tag runs when branch pushes start.
4. [pending] Verify syntax, full CI status and native package validation before fast-forwarding dev to main; inspect accumulated product commits separately.

## Runner policy
- Continue GitHub-hosted ubuntu-24.04 for the public repository, with no private self-hosted secrets.
- Cross-OS macOS/Windows jobs, if introduced, must use native GitHub-hosted images and cannot be replaced with Linux containers.
- RunnerRouter is not required for public NativePair and must not receive an automatic self-hosted route.

## Rollback
Revert the isolated CI commit on dev; preserve main and tags without force-pushing.

## Reproduced binary-order failure and corrective plan

The earlier dev run `39089996466` failed 26 Python binary integration contracts after running 1,869 tests: the suite requires native binaries produced by `cargo build --workspace --locked`. The quick Rust job incorrectly invoked this full Python inventory before the package job; the package job is intentionally tag-only. The confirmed root cause is a missing binary build prerequisite, not a failed functional assertion. Keep syntax checks on each dev push, run all executable Python contracts in the tagged package job **after** its existing workspace build step, and keep the packaging/install smoke and full tests unchanged. Re-run the dev CI on the exact new SHA. Release-tag acceptance is not claimed before a real annotated current-main tag run.

