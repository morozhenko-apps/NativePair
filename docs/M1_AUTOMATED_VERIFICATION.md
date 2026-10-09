# M1 automated verification execution record

Date: 2026-10-09. Branch: `dev`. Mode: **B — Testing**.
User-selected scope: finish automated M1 verification, fix exposed defects, and
run the deterministic suite ten consecutive times. Live calls, SMS, device
permission changes, service restarts and iPhone experiments are excluded.

## Repository scan and baseline

Production: three Rust sources, fourteen protocol/audio Bash probes, one Python
observer, a Bash observer entry point, two packaging scripts, Debian control
template and CI. There is no production D-Bus daemon, GUI, persistence layer,
network HTTP client, billing or ANCS adapter yet. Do not invent tests for them.
All existing production sources and required agent/architecture/privacy/roadmap
guides were read. Trivial enum declarations are included in the domain cross
product, rather than used as a substitute for protocol coverage.

Baseline: five Rust tests and seventeen Python test methods. The seventeen
Python methods passed locally in 11.700 seconds. Rust baseline is pending the
quality gate. Prior 196-scenario forecast is superseded by executable scenario
inventory for existing code; hardware forecasts remain separate.

Local commands: `cargo fmt --all -- --check`,
`cargo clippy --workspace --all-targets --all-features -- -D warnings`,
`cargo test --workspace --all-features`,
`python3 -m unittest discover -s scripts/tests -v`,
`bash -n scripts/<name>.sh`, `./scripts/build-deb.sh`, and
`./scripts/verify-deb.sh artifacts/nativepair_<version>_<arch>.deb`.
CI currently separates Rust and Debian jobs and selects only two Python files;
the final gate must discover the complete Python suite.

## Invariants and decisions

- External command fakes replace BlueZ, OBEX, PipeWire and packaging tools;
  actual Bash/Python/Rust production logic is executed without domain mocks.
- Use a hermetic PATH and synthetic identifiers. No test may fall through to
  real Bluetooth, D-Bus, phone, journal or audio commands.
- Conditions and scripted external responses drive polling tests. Fake waiting
  advances test events; tests never wait for wall-clock device behavior.
- No preflight calls Dial, HangupAll, Activate or PushMessage. One send/dial
  attempt is the maximum; ambiguous replies never cause automatic re-send.
- Existing calls are never modified. Attempted owned calls receive bounded
  cleanup after failures/signals; successful hangup avoids duplicate cleanup.
- Personal identifiers, payloads, raw errors and arbitrary upstream state
  strings must not escape diagnostics. Temporary artifacts are private and
  removed after success, failure and interruption.
- Malformed external data cannot be reported as proven support or crash with
  a payload-bearing traceback. Unknown and inconclusive remain distinct from
  confirmed success.
- MAP transfer completion must refer to the returned transfer object; a
  different concurrent transfer cannot confirm this SMS. No protocol/API or
  security boundary is introduced by correcting this evidence defect.
- Packaging tests use temporary copies/roots and never install on this host.
  Real build/extract/binary smoke verifies the current host architecture.
- Test-only tooling is Python standard library plus existing Rust/Debian tools.
  No new runtime dependency or product feature is planned.

## Milestones and rollback

1. **Analysis and planning — complete:** complete artifact inventory, source
   branch map, applicability matrix, interaction cases and estimates before
   writing tests. Commit the documentation as the rollback baseline.
2. **Domain and observer — core/observer complete, binary contracts in stage 4:** exhaustive capability state cross product; CLI
   arguments; observer parsers, graph, subprocess, sample, clocked lifecycle,
   privacy and malformed data. Fix only exposed correctness defects. Commit.
3. **Protocol contract harness and probes:** hermetic external commands;
   parameter/guard branches, all command failure exits, MAP/PBAP lifecycle,
   event/send correlation, HFP/SCO states and cleanup, audio/SDP/MNS diagnostics.
   Commit coherent groups with updated execution state.
4. **Packaging and CI:** metadata/layout/checksum/error contracts; real package
   smoke; CI discovers all deterministic tests. Commit.
5. **Verification and handoff:** mutation review, per-file coverage map, full
   quality gate, ten consecutive runs, CI verification where accessible,
   categorized actual counts and remaining hardware gates. Commit records.

Each milestone is reversible with its atomic commit. No promotion to `main`
and no push is required to implement the local test scope. GitHub CI can be
checked for the existing baseline; new remote execution requires publishing
the commits, and must be reported separately from local results.

## Exhaustive artifact inventory and planned assertion families

Every named function plus top-level execution belongs to a family below.
Expected counts are lower-bound scenario estimates, not results. Parameters
are expanded where boundaries share a branch; every independent outcome must
have an assertion. Source-level branch locations are in the companion map.

| Family / production artifact | Methods / rules | Risk; level; expected scenarios |
| --- | --- | --- |
| CORE: `nativepair-core/src/lib.rs` | new, platform, availability, set_availability, supports; all 3 platforms × 5 capabilities × 4 states × 4 transitions; isolation, previous values, repeated updates | High false support; unit; 300+ |
| CLI: `nativepair-cli/src/main.rs` | main; empty, both help/version aliases, unknown, extra arguments | Medium public exit contract; integration; 12+ |
| DAEMON: `nativepair-daemon/src/main.rs` | main; empty, both version aliases, unknown, extra arguments | Medium public exit contract; integration; 8+ |
| WATCH: `probe_call_audio_watch.py` | command, parse_wpctl_id, parse_sink_mute, is_bluetooth, graph_snapshot, nested props, find_gateway, call_present, sample, emit, main | High privacy/corrupt graph; unit; 90+ |
| WATCH-ENTRY: `probe-call-audio-watch.sh` | argument forwarding, Python exit propagation | Low wrapper; integration; 3+ |
| BT: `probe-bluetooth.sh` | usage, command_present, bool_line, property_is_yes, uuid_present, top-level | Medium discovery/privacy; contract; 30+ |
| SESSION: `probe-obex-session.sh` | usage, cleanup, wait_for_log, top-level target/session validation | High lifetime/privacy; contract; 30+ |
| READ: `probe-obex-read.sh` | usage, cleanup, wait_for_log, array_count, dbus_error_name, call_to_file, MAP and PBAP operations | High bounded reads; contract; 45+ |
| SEND: `probe-map-send.sh` | usage, cleanup, wait_for_log, bMessage generation/framing, transfer observation, top-level guards | High money/privacy/duplicate SMS; contract; 40+ |
| EVENTS: `probe-map-events.sh` | usage, cleanup, wait_for_log, registration, baseline/event observation | High false event evidence/privacy; contract; 25+ |
| SDP: `probe-map-sdp.sh` | usage, SDP command status, all four independent attribute checks | Medium malformed SDP; contract; 15+ |
| MNS: `probe-mns.sh` | command_present, bool_line, process/plugin/signature/profile/SDP classification, upstream defect pattern | Medium environment diagnosis; contract; 20+ |
| HFP: `probe-hfp.sh` | usage, cleanup, bool_line, manager/gateway/call/API/discovery rules | High capability evidence; contract; 25+ |
| AUDIO: `probe-hfp-audio.sh` | usage, cleanup, bool_line, transport State/Codec/RejectSCO parsers | High policy/codec; contract; 25+ |
| CALL: `probe-hfp-call.sh` | usage, cleanup, bool_line, no-call guard, Dial, observation, HangupAll | High owned-call cleanup; contract; 30+ |
| SCO: `probe-hfp-sco.sh` | usage, cleanup, bool_line, read_transport_state, refresh_call_snapshot, inspect_hfp_nodes, activation state machine | Critical call/audio/privacy; contract; 55+ |
| ROUTING: `probe-audio-routing.sh` | cleanup, gateway/state/default-node/HFP classification; embedded Python | High false routing claims; contract; 20+ |
| HEALTH: `probe-audio-health.sh` | cleanup; embedded props_for, is_bluetooth, is_hfp, media_class, default_kind; top parsing/growth/classification/journal | High diagnostic correctness/privacy; contract; 35+ |
| BUILD: `build-deb.sh` | version, architecture, staging, release build, source epoch, checksum | High destructive staging/package integrity; integration; 15+ |
| VERIFY: `verify-deb.sh` | assert_field, dependency_present; input/checksum/metadata/layout/executable guards | High package integrity; integration; 20+ |

## Positive / negative applicability matrix

`?` = planned for all applicable rules in the family. `—reason` = not
applicable. No cell is empty. N3 covers local IPC/tool failures rather than
inventing HTTP/DNS contracts; N11 is absent throughout M1.

| Family | Positive | N1 | N2 | N3 | N4 | N5 | N6 | N7 | N8 | N9 | N10 | N11 | N12 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CORE | ? | —typed API | ? | —pure | ? | —exclusive mutable borrow | —no serialization | —no auth | —no time | —pure | ? | —no billing | —no I/O |
| CLI/DAEMON | ? | ? | ? | —no IPC yet | —stateless | —stateless | —no serialized input | —no auth | —no time | —immediate | ? | —no billing | —no storage |
| WATCH/ENTRY | ? | ? | ? | ? | ? | ? | ? | ? | ? | ? | ? | —no billing | —memory only |
| BT | ? | ? | ? | ? | —read only | —snapshot | ? | ? | —no time | —no owned resource | ? | —no billing | —no temp |
| SESSION/READ | ? | ? | ? | ? | —read only | ? | ? | ? | —no dates | ? | ? | —no billing | ? |
| SEND | ? | ? | ? | ? | ? | ? | ? | ? | —fixed ASCII | ? | ? | —no entitlements | ? |
| EVENTS | ? | ? | ? | ? | ? | ? | ? | ? | —counts only | ? | ? | —no billing | ? |
| SDP/MNS | ? | ? | ? | ? | —read only | —snapshot | ? | ? | —no dates | ? | ? | —no billing | ? |
| HFP/AUDIO | ? | ? | ? | ? | ? | ? | ? | ? | —no dates | ? | ? | —no billing | ? |
| CALL/SCO | ? | ? | ? | ? | ? | ? | ? | ? | —no dates | ? | ? | —no billing | ? |
| ROUTING/HEALTH | ? | ? | ? | ? | —snapshot | ? | ? | ? | ? | ? | ? | —no billing | ? |
| BUILD/VERIFY | ? | ? | ? | ? | ? | —single staging owner | ? | ? | ? | ? | —synthetic paths | —no billing | ? |

## Interaction matrix (subset, never extra count)

- CORE: platform × capability × old state × new state; unrelated capability
  preservation and repeated assignments.
- WATCH: sink/source missing × graph state × link state; repeated snapshots ×
  call/mute/HFP/route changes; invalid samples between valid snapshots; interrupt.
- OBEX: target × connect outcome × interface/proxy × malformed/empty listing;
  operation failure × cleanup and payload redaction; process exit × polling.
- SEND: accepted push × matching/unrelated/replayed/error event × lost session;
  preflight × generated CRLF/length/private payload × no PushMessage.
- EVENTS: registration complete/error/unknown × new monitor/obex event ×
  baseline existing event × process exit.
- HFP/SCO: existing call × dial flag; call state × transport state × method
  reply; pending/failed activation × readback × node readiness × cleanup;
  missing/replaced call object × fallback interface; failed hangup × cleanup.
- AUDIO: codec × RejectSCO × malformed state; device/profile/role filtering ×
  default routing; top counters grow/reset × run state × Bluetooth/media role.
- PACKAGE: architecture × version × checksum × metadata/layout; individual
  missing dependency/doc/binary × verifier outcome; staging/build failure.

## Mutation review plan

### Defects exposed during protocol work

- Ten probes echoed arbitrary unknown arguments. The privacy regression tests
  failed for every probe; errors now omit the argument value.
- Add `probe_obex_monitor.py` as an internal pure parser for busctl monitor
  messages (functions: transfer_status, main). It must accept only a valid
  returned session/transfer path and a matching PropertiesChanged Status
  variant. Missing/truncated/malformed/unrelated events remain unknown;
  matching error is terminal. Unit inventory: 20+ framing, path, status,
  duplicate/ordering, error, corruption and file-I/O scenarios. Contract
  inventory: preflight, single send, ambiguous push, complete/error/unrelated
  transfer, session loss, no path, private payload, mode/CRLF/LENGTH.
- Temporary FIFO creation currently precedes cleanup installation in four
  OBEX scripts. Install the trap before that fallible operation, and give
  INT/TERM explicit non-success exit codes while sharing EXIT cleanup.
- OBEX array parsing must distinguish empty/malformed replies from real zero
  counts and avoid shell arithmetic overflow on malformed oversized counts.
- Session failure output must use a fixed error category; arbitrary remote
  text and target strings cannot be printed as privacy-safe diagnostics.
- Actual regression failures confirmed FIFO leaks in all four OBEX probes,
  empty-count false negatives, numeric overflow and arbitrary target output.
  Counters now require the correct wire signature and wire-width bounds;
  oversized arrays and PBAP q values are unknown, never valid size evidence.
- A killed obexctl caused SIGPIPE inside cleanup, terminating Bash before
  deletion. Ignore PIPE only within teardown and preserve the original exit
  status. INT/TERM use 130/143. Monitor startup now waits for busctl's observed
  readiness line instead of a fixed 300 ms sleep (the installed busctl binary
  confirms this readiness text).

Assertions must kill: available != available, wrong previous value/isolation,
inclusive/exclusive numeric bounds, absent no-call guard, removed hangup,
duplicate dial/send, unconditional successful transfer, unrelated-transfer
acceptance, pending-to-Activate race, missing source/sink filtering, > versus
>= counter growth, wrong codec, raw upstream error/state output, checksum skip,
missing dependency/layout check. Actual trials and surviving mutations are
recorded after execution. No percentage is claimed without instrumentation.

## Execution state

- Baseline Python suite: passed; process completed and terminal session closed.
- Core: three added Rust test methods execute 495 table rows (15 initial-state,
  240 transitions, 240 independence/clone rows); all eight Rust methods pass.
- Observer: 149 added independent table-driven unittest scenarios pass in
  0.077 seconds. Clock and subprocess adapters are fake; parsers and lifecycle
  execute production code. Existing five observer tests remain.
- Exposed observer defects fixed: corrupt graph entries no longer raise
  payload-bearing exceptions; stale default IDs no longer mean present nodes;
  volume parser rejects malformed strings; gateway/call paths match complete
  quoted object paths; malformed call replies produce unknown.
- Ignore generated bytecode, scratch and package artifacts to keep handoff
  status limited to source changes. No runtime dependency was added.
- Protocol harness replaces every external service command through a
  hermetic PATH, owns its subprocess group, and asserts no leftover temporary
  directories and no synthetic private markers in either output stream.
- Latest isolated runs: 340 parameter cases passed before adding the monitor
  Python dependency case; 72 discovery cases passed; 97 OBEX + 33 monitor-parser
  cases passed; 26 MAP-send cases passed in 9.711 seconds after fixing readiness
  and SIGPIPE. Full combined verification remains pending.
- Hardware: no new operation performed; ADB visibility is not test coverage.
- Completion gate: open until inventory, branches, tests, mutation review,
  quality checks and ten consecutive runs have evidence.
