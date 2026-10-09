# M1 automated verification execution record

Date: 2026-10-09. Branch: `dev`. Mode: **B — Testing**.

Latest user refinement: run static checks and deterministic Rust/Python cases
once, rather than ten times. The stability lane repeats only real background
OBEX/FIFO/session teardown and synthetic OS-signal scenarios ten times. No
currently failing flaky test is hidden or skipped. This supersedes the earlier
whole-suite repeat policy for this task; CI still runs the complete suite once.

Final observer audit (before implementation): enforce uint32 node IDs, reject
non-string/oversized wpctl ID replies and malformed false-valued info/props.
Only the exact empty GetCalls array establishes absence; a positive count
without a whole call object for the selected gateway remains unknown. Apply
the same fail-closed distinction to the passive HFP diagnostic. Add explicit
boundary/type/corruption/correlation rows; valid output schemas are unchanged.
User-selected scope: finish automated M1 verification, fix exposed defects, and
run the deterministic suite ten consecutive times. Live calls, SMS, device
permission changes, service restarts and iPhone experiments are excluded.

## Repository scan and baseline

Production: three Rust sources, fourteen Bash probe/observer entry points,
three Python observer/parser modules, two packaging scripts, Debian control
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
Baseline CI separated Rust and Debian jobs and selected only two Python files;
the updated gate discovers the complete Python suite after building binaries.

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
3. **Protocol contract harness and probes — implemented; stability gate pending:** hermetic external commands;
   parameter/guard branches, all command failure exits, MAP/PBAP lifecycle,
   event/send correlation, HFP/SCO states and cleanup, audio/SDP/MNS diagnostics.
   Commit coherent groups with updated execution state.
4. **Packaging and CI — implemented; remote CI not executed:** metadata/layout/checksum/error contracts; real package
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
| GRAPH: `probe_audio_graph.py` | valid_nodes, load_nodes; root/entry/info/props/ID validation, duplicates, file errors | High false endpoints; unit; 30+ |
| MONITOR: `probe_obex_monitor.py` | transfer_status, registration, message_count, main; framing, correlation, replay, errors, CLI modes | High false send/event evidence; unit; 50+ |

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

HFP/audio test stage extends the existing invariants, without selecting any
audio-routing architecture: malformed GetCalls replies cannot authorize Dial;
ambiguous gateway enumeration cannot select an arbitrary phone; transport and
call state diagnostics accept only known enums. Corrupt JSON and malformed
node entries produce anonymous unavailable results, and duplicate endpoint IDs
cannot establish two distinct SCO endpoints. Scripted signals test cleanup of
owned synthetic calls only. MNS's known upstream-defect pattern must exclude an
explicitly disabled MNS plugin, as already required by FEASIBILITY.md.

Minimal testability extraction: `probe_audio_graph.py` owns `load_nodes(path)`
and `valid_nodes(data)` for the three embedded audio classifiers. Its contract
requires a JSON array, filters malformed/non-node/invalid-ID entries, normalizes
missing info/props to dictionaries, and resolves duplicate IDs by the last
snapshot entry. Unit inventory: null/scalar/root shapes; invalid object/info/
props/ID types; empty/one/many nodes; duplicates; Unicode and unreadable/corrupt
files (30+ scenarios, N1/N2/N6/N10/N12). The Bash tools pass their own script
directory explicitly, so invocation from another working directory still works.
This avoids three incompatible corruption policies and adds no dependency.

Packaging verification stage: exercise both binary entry points and real
temporary Debian archives. Build tests use a temporary repository copy and
fake Cargo compilation only; verifier tests execute the actual dpkg and
checksum tooling, with synthetic executable payloads. Verify every required
metadata/dependency/doc/binary independently, checksum corruption/missing/wrong
target/multiline sidecars, invalid versions/architectures, build/tool/staging
failures and source-date handling. A package cannot be relabelled as another
architecture without cross-compiling: this build script is native-only and
must reject an override different from dpkg's host architecture. A SHA sidecar
must name this exact archive, not merely some other file whose hash is valid.
Preserve nonzero exit statuses from external tools (e.g. dpkg-deb returns 2
for malformed archive magic); usage errors are 2 and NativePair guard failures
are 1. Tests assert the concrete expected tool code rather than rewriting all
external failures to an invented uniform status.

MAP event parser extension (before implementation): `message_count(text,
session, obexctl=False)` counts additions within this session, suppresses
duplicate additions, and recognizes removals before path reuse;
`registration(text, session)` correlates transfer evidence to this session.
The monitor CLI gains internal message/registration modes. Planned unit and
contract cases cover other-session events, existing baseline events, duplicates,
remove/re-add, both monitor and obexctl sources, all registration outcomes and
monitor/session death. No SMS is generated by these fixtures.

Numeric overflow contract: diagnostic second values must fit the existing
signed 64-bit shell arithmetic after conversion to tenths of a second. Reject
values above 922337203685477580 before any external operation; this is an
implementation-capacity guard, not a new product timeout policy. Add max-1,
max, max+1 and oversized-digit regression rows for every timer variable.

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

Final branch audit extension (before implementation): require ObjectManager
interface framing for message additions/removals and signal/interface/member
framing for registration-transfer presence. A body from an unrelated interface
or method return must not establish evidence. Add explicit malformed-framing
regressions. Packaging supplements cover each required missing tool, malformed
Cargo metadata, failed staging/archive/hash commands, epoch absent/derived/
invalid and overridden artifact/staging directories. Binary argument errors
are categorized as N1, separately from successful entry-point behavior.
Mutation trials use disposable repository copies only, with baseline tests
passing first; production sources are never mutated in the working checkout.
The observer entry wrapper is tested separately for exact argv forwarding,
success/failure/interrupt exit propagation and missing Python. Epoch fixtures
are categorized as N8 because they verify reproducible timestamps independent
of local calendar rendering; no date/locale product feature is invented.
Mutation review exposed a test-harness assertion defect: searching for a field
as a substring can match a longer field ending in that name (for example,
`nodes_with_err_growth` inside `bluetooth_nodes_with_err_growth`). Replace field
substring checks with exact output-line membership; rerun affected baselines
and mutations. Assertions are strengthened, not adjusted to accept a bug.
Verification instrumentation uses standard-library Python line/arc tracing
and Bash DEBUG source-line traces during one complete run. It records executed
locations without printing command arguments or values. These traces help the
manual branch audit; they are not an instrumented 100% branch-coverage claim.
The first instrumented complete run passed (1295 Python methods, 313.683s).
Audit then identified non-canonical zero-prefixed OBEX numeric replies such as
`08`: Bash arithmetic treats them as octal. Add 12 independent regression rows
for MAP folders/messages, PBAP lists and PBAP size using `00`, `01`, `08`;
require unknown for these malformed busctl decimal forms before shell
arithmetic. Stop only the owned stability-run process group and restart all
ten runs after this source change. The interrupted run is not a flaky failure.
The completed trace also prompts explicit coverage of both INT and TERM trap
arms for every probe owning temporary files/processes. Add independent signal
rows at an external operation after trap installation; assert exact exit status,
zero unwanted mutations and no leftover artifacts. These are synthetic signals
to owned fixture processes, never signals to host services.
Signal-fixture correction: an external command inside Bash command substitution
has a subshell parent, so signaling its immediate parent does not test the
probe's INT trap. The harness launcher records its owned PID before exec; the
new `signal_probe` adapter option targets that recorded probe PID. Existing
`signal_parent` fixtures retain their meaning. This changes test infrastructure
only and makes trap-arm assertions exercise the intended process.
Signal audit exposed ignored INT in SDP/MNS (successful exit after cancellation).
Add explicit INT/TERM exits (130/143) before operations, retaining EXIT cleanup.
The same cancellation invariant applies to build/verify: a cancelled operation
must not report success or publish a finished package. Add two signal cases
per packaging entry point; verifier temp extraction must be removed. Build
staging is intentionally persistent and cleared by the next build, as before.

- Combined Python run: 1180 tests passed in 273.046 seconds; process completed
  and terminal session closed. The 68 subsequently added branch rows passed
  separately in 12.512 seconds. A fresh combined run is required after the
  final parser and packaging audit changes.

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

## Canonical implemented inventory

The [canonical Python inventory](evidence/m1-automated-test-inventory.json)
contains 1363 uniquely named methods, including 17 existing methods. The
implementation added 1346 Python scenarios and three Rust methods containing
495 table rows. Method counts, table rows and assertions have separate units;
do not add them together as a coverage percentage.

| Primary category | Complete Python suite | Added Python scenarios |
| --- | ---: | ---: |
| Positive | 231 | 222 |
| N1 input validation | 294 | 294 |
| N2 boundaries | 133 | 132 |
| N3 IPC/tool failures | 151 | 148 |
| N4 replay/idempotency | 23 | 23 |
| N5 races/state changes | 23 | 20 |
| N6 corrupt/stale data | 260 | 260 |
| N7 permissions/guards/missing tools | 147 | 146 |
| N8 reproducible epoch | 3 | 3 |
| N9 interruption | 36 | 36 |
| N10 privacy | 22 | 22 |
| N11 entitlements | 0 (not applicable) | 0 |
| N12 storage/cleanup failures | 40 | 40 |
| **Total** | **1363** | **1346** |

Each method has one primary category. Other invariants asserted by the same
test (privacy, no duplicate mutation and cleanup) are not counted a second time.
The Rust table rows cover all 15 platform/capability initial combinations,
240 old/new transitions and 240 independent-capability/clone combinations.
Sixty transition rows reassign the same value; all four states and all five
capabilities participate. The original five Rust tests are retained.

N11 is absent because there is no billing or entitlement implementation.
HTTP/DNS/status-code variants of N3, authorization tokens of N7, migrations of
N6/N12, UI dialogs/rotation of N9 and calendar/DST/currency behavior of N8 are
not applicable to the existing sources. Local IPC errors, absent tools,
malformed snapshots, signals and package epochs are tested instead. Hardware
permission UX, recovery after service restart and iPhone ANCS are separate
feasibility work, not covered by simulated evidence.

The existing source distribution is dominated by executable protocol probes,
so integration/contract tests exceed the preferred product pyramid ratio.
Pure core/parser/observer rules are tested at unit level; hardware E2E count is
zero. No artificial DTO tests or hypothetical daemon/UI tests were added to
improve a ratio. Unit/domain tests complete in fractions of a second; shell
contracts take most of the complete-suite duration.

## Actual mutation review

All 29 deliberately injected mutations were killed by assertion failures;
every trial first passed the same test selection on unmodified copied sources.
This is a finite invariant review, not an exhaustive mutation score.

| Mutation | Assertion protecting the invariant |
| --- | --- |
| capability_available_inverted | exact supports result for all states |
| transition_previous_value_discarded | exact old state for every transition |
| unrelated_transfer_accepted | another transfer remains unknown |
| unrelated_event_interface_accepted | wrong ObjectManager interface has zero events |
| duplicate_sms_send | exactly one PushMessage |
| sms_retry_enabled | Retry argument is false |
| ambiguous_dial_cleanup_removed | attempted owned call receives HangupAll |
| pending_transport_activated_twice | pending state invokes zero Activate calls |
| single_endpoint_proves_duplex | both distinct source and sink are required |
| zero_error_growth_counted | exact full-line zero-growth count |
| timer_maximum_rejected | maximum arithmetic-safe value passes validation |
| wrong_archive_sidecar_accepted | sidecar must name the inspected archive |
| runtime_dependency_not_checked | each required dependency is independent |
| duplicate_node_ids_accepted | duplicate ID resolves to one latest node |
| private_argument_printed | synthetic private value absent from both streams |
| codec_mapping_changed | byte codec 1 maps to CVSD |
| temporary_artifacts_not_removed | no temporary artifacts after interruption |
| duplicate_owned_call_dial | exactly one Dial |
| preflight_no_dial_guard_removed | preflight invokes zero Dial/HangupAll |
| zero_prefixed_array_count_accepted | malformed array decimal remains unknown |
| zero_prefixed_phonebook_size_accepted | malformed PBAP size remains unknown |
| sdp_interrupt_ignored | interrupted SDP exits 130 |
| mns_interrupt_ignored | interrupted MNS exits 130 |
| build_interrupt_ignored | interrupted build emits no finished package |
| verify_interrupt_ignored | interrupted verification cannot report success |
| watcher_node_id_overflow_accepted | uint32-overflow graph node is absent |
| watcher_false_graph_properties_accepted | malformed graph object is absent |
| watcher_malformed_calls_reported_absent | corrupt call reply remains unknown |
| passive_hfp_malformed_calls_reported_absent | corrupt passive reply remains unknown |

The initial zero-growth mutation survived a substring-based harness assertion.
Exact line matching killed it on rerun. That surviving trial is resolved and
recorded here rather than omitted from the review history. Reproduce using
`python3 scripts/tests/review_mutations.py --output work/mutation-review.json`.

## Validation and handoff gate

Formatting and Clippy passed. The ten-run stability gate is in progress;
`work/repeated-runs.json` records only completed runs. Shell syntax, executable
bits and Python compilation passed. The actual amd64 release package built
and passed metadata, layout, checksum and both extracted binary smoke checks.
All completed shell commands/process sessions were closed (Terminal closed).
The first draft stability series was deliberately interrupted after one pass
to fix the numeric and signal defects above; it does not count toward the final
ten-run gate. Final source state requires one fresh complete baseline and nine further
process stability lane runs, as refined by the user below.
GitHub execution for these local commits has not been triggered or verified.
No host package installation and no live phone operation were performed.

### Process stability lane refinement (2026-10-09)

The user requested that static and deterministic checks not be repeated ten
times. `run_suite.py --runs 10` now runs Rust and the complete 1363-method Python
baseline once, then repeats exactly 182 subprocess/FIFO/interruption scenarios
nine times. Those scenarios therefore receive ten consecutive executions.
The selector includes ObexContracts (109), SendContracts (26), MapEventContracts
(15), RemainingProbeContracts N9 (24), HFP dial interruption cases (4), and
PackagingBranches N9 (4). Pure event parsing, fake-clock observer states and
simulated transport transitions run once. No failure is classified away as
flaky. Reports identify the lane for each run and save both canonical inventories.

The latest observer regressions add 32 scenarios: canonical uint32 node IDs,
malformed graph properties, exact empty call arrays and selected-gateway call
objects. The watcher rejects malformed IDs/properties and both passive HFP
observers report `unknown` rather than claiming no call from malformed data.
These internal parsing fixes retain the existing output schema. The targeted
174 watcher and seven passive HFP corruption cases pass.
