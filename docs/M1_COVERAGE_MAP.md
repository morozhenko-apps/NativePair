# M1 functional coverage and handoff map

Date: 2026-10-09. Scope: all 22 current production source files.

Functions include embedded Python and top-level entry behavior. Each row maps
its independent contract branches to executable assertion families. Exact
scenario IDs and categories are in the [canonical inventory](evidence/m1-automated-test-inventory.json);
inputs and expected states/side effects are in those test sources. The
[source decision index](M1_BRANCH_MAP.md) records individual source locations.
This functional review is not an instrumented 100% branch coverage percentage.

| Production file | Functions (plus entry point) | Covered branch families | Tests | Remaining and reason |
| --- | --- | --- | --- | --- |
| [scripts/build-deb.sh](../scripts/build-deb.sh) | top-level | tool guards; version and native architecture; epoch; staging/build/archive/hash failures; output; INT/TERM | [test_packaging_contract](../scripts/tests/test_packaging_contract.py), [test_packaging_branches](../scripts/tests/test_packaging_branches.py) | No remaining planned automated contract; native behavior on other host architectures/platforms is outside this run. |
| [scripts/verify-deb.sh](../scripts/verify-deb.sh) | assert_field, dependency_present | input and checksum target; every metadata/dependency/layout field; binary smoke; tool/extract failures; INT/TERM | [test_packaging_contract](../scripts/tests/test_packaging_contract.py), [test_packaging_branches](../scripts/tests/test_packaging_branches.py) | No remaining planned automated contract; native behavior on other host architectures/platforms is outside this run. |
| [scripts/probe-audio-health.sh](../scripts/probe-audio-health.sh) | cleanup, props_for, is_bluetooth, is_hfp, media_class, default_kind | iterations; corrupt/empty snapshots; every Bluetooth/profile/media/default classification; counters reset/grow/zero; journal allowlist; cleanup | [test_audio_diagnostics_contract](../scripts/tests/test_audio_diagnostics_contract.py), [test_probe_parameters](../scripts/tests/test_probe_parameters.py), [test_remaining_contracts](../scripts/tests/test_remaining_contracts.py) | Real device/service interoperability and hardware timing remain unverified; synthetic contracts cannot prove them. |
| [scripts/probe-audio-routing.sh](../scripts/probe-audio-routing.sh) | cleanup | gateway and call states; graph/default IDs; source/sink/profile/device filters; malformed data; command failures; cleanup | [test_audio_diagnostics_contract](../scripts/tests/test_audio_diagnostics_contract.py), [test_probe_parameters](../scripts/tests/test_probe_parameters.py), [test_remaining_contracts](../scripts/tests/test_remaining_contracts.py) | Real device/service interoperability and hardware timing remain unverified; synthetic contracts cannot prove them. |
| [scripts/probe-bluetooth.sh](../scripts/probe-bluetooth.sh) | usage, command_present, bool_line, property_is_yes, uuid_present | argument and tool guards; paired/trusted/connected values; independent UUIDs; anonymous counts; command failures | [test_discovery_contract](../scripts/tests/test_discovery_contract.py), [test_probe_parameters](../scripts/tests/test_probe_parameters.py), [test_remaining_contracts](../scripts/tests/test_remaining_contracts.py) | Real device/service interoperability and hardware timing remain unverified; synthetic contracts cannot prove them. |
| [scripts/probe-call-audio-watch.sh](../scripts/probe-call-audio-watch.sh) | top-level | Python availability; exact argv; success/error/interrupt exit propagation | [test_watcher_entry](../scripts/tests/test_watcher_entry.py) | No remaining planned automated contract; native behavior on other host architectures/platforms is outside this run. |
| [scripts/probe-hfp.sh](../scripts/probe-hfp.sh) | usage, cleanup, bool_line | target/connect/tools; manager/gateway uniqueness; interfaces/methods; selected-gateway call presence and corruption; signal cleanup | [test_hfp_contract_extended](../scripts/tests/test_hfp_contract_extended.py), [test_probe_parameters](../scripts/tests/test_probe_parameters.py), [test_remaining_contracts](../scripts/tests/test_remaining_contracts.py) | Real device/service interoperability and hardware timing remain unverified; synthetic contracts cannot prove them. |
| [scripts/probe-hfp-audio.sh](../scripts/probe-hfp-audio.sh) | usage, cleanup, bool_line | target/gateway/interfaces; every State/Codec/RejectSCO classification and query failure; signal cleanup | [test_hfp_contract_extended](../scripts/tests/test_hfp_contract_extended.py), [test_probe_parameters](../scripts/tests/test_probe_parameters.py), [test_remaining_contracts](../scripts/tests/test_remaining_contracts.py) | Real device/service interoperability and hardware timing remain unverified; synthetic contracts cannot prove them. |
| [scripts/probe-hfp-call.sh](../scripts/probe-hfp-call.sh) | usage, cleanup, bool_line | preflight no mutation; GetCalls guard; existing call untouched; one Dial; missing/ambiguous call; explicit/cleanup hangup; INT/TERM | [test_hfp_contract_extended](../scripts/tests/test_hfp_contract_extended.py), [test_hfp_probe_contract](../scripts/tests/test_hfp_probe_contract.py), [test_probe_parameters](../scripts/tests/test_probe_parameters.py), [test_remaining_contracts](../scripts/tests/test_remaining_contracts.py) | Real device/service interoperability and hardware timing remain unverified; synthetic contracts cannot prove them. |
| [scripts/probe-hfp-sco.sh](../scripts/probe-hfp-sco.sh) | usage, cleanup, bool_line, read_transport_state, refresh_call_snapshot, inspect_hfp_nodes | call ownership; transport policy/interface; pending/active/idle/error transitions; activation failure; call fallback; distinct duplex nodes; cleanup | [test_hfp_contract_extended](../scripts/tests/test_hfp_contract_extended.py), [test_hfp_probe_contract](../scripts/tests/test_hfp_probe_contract.py), [test_probe_parameters](../scripts/tests/test_probe_parameters.py), [test_remaining_contracts](../scripts/tests/test_remaining_contracts.py) | Real device/service interoperability and hardware timing remain unverified; synthetic contracts cannot prove them. |
| [scripts/probe-map-events.sh](../scripts/probe-map-events.sh) | usage, cleanup, wait_for_log | preflight; session/registration/transfer states; matching ObjectManager additions; baseline/replay/removal; monitor exit; FIFO/signal cleanup | [test_map_events_contract](../scripts/tests/test_map_events_contract.py), [test_obex_contract](../scripts/tests/test_obex_contract.py), [test_probe_parameters](../scripts/tests/test_probe_parameters.py), [test_remaining_contracts](../scripts/tests/test_remaining_contracts.py) | Real device/service interoperability and hardware timing remain unverified; synthetic contracts cannot prove them. |
| [scripts/probe-map-sdp.sh](../scripts/probe-map-sdp.sh) | usage | arguments/tools/connect; four independent SDP attributes; corrupt/private reply; INT/TERM | [test_discovery_contract](../scripts/tests/test_discovery_contract.py), [test_probe_parameters](../scripts/tests/test_probe_parameters.py), [test_remaining_contracts](../scripts/tests/test_remaining_contracts.py) | Real device/service interoperability and hardware timing remain unverified; synthetic contracts cannot prove them. |
| [scripts/probe-map-send.sh](../scripts/probe-map-send.sh) | usage, cleanup, wait_for_log | preflight; one push and Retry=false; bMessage CRLF/length/framing; matching/unrelated/error transfer; private content; FIFO/signal cleanup | [test_map_send_contract](../scripts/tests/test_map_send_contract.py), [test_obex_contract](../scripts/tests/test_obex_contract.py), [test_probe_parameters](../scripts/tests/test_probe_parameters.py), [test_remaining_contracts](../scripts/tests/test_remaining_contracts.py) | Real device/service interoperability and hardware timing remain unverified; synthetic contracts cannot prove them. |
| [scripts/probe-mns.sh](../scripts/probe-mns.sh) | command_present, bool_line | tool/process/plugin discovery; exact disable flags; compiled signatures; session profile/SDP; upstream defect classification; INT/TERM | [test_discovery_contract](../scripts/tests/test_discovery_contract.py), [test_mns_process_contract](../scripts/tests/test_mns_process_contract.py), [test_remaining_contracts](../scripts/tests/test_remaining_contracts.py) | Real device/service interoperability and hardware timing remain unverified; synthetic contracts cannot prove them. |
| [scripts/probe-obex-read.sh](../scripts/probe-obex-read.sh) | usage, cleanup, wait_for_log, array_count, dbus_error_name, call_to_file | target/timer/tools; MAP/PBAP command successes and failures; signatures and canonical bounded counts; unknown/empty arrays; FIFO/signal cleanup | [test_obex_contract](../scripts/tests/test_obex_contract.py), [test_probe_parameters](../scripts/tests/test_probe_parameters.py), [test_remaining_contracts](../scripts/tests/test_remaining_contracts.py) | Real device/service interoperability and hardware timing remain unverified; synthetic contracts cannot prove them. |
| [scripts/probe-obex-session.sh](../scripts/probe-obex-session.sh) | usage, cleanup, wait_for_log | target/timer/tools; session success/error/disconnect/proxy/private reply; bounded polling and FIFO/signal cleanup | [test_obex_contract](../scripts/tests/test_obex_contract.py), [test_probe_parameters](../scripts/tests/test_probe_parameters.py), [test_remaining_contracts](../scripts/tests/test_remaining_contracts.py) | Real device/service interoperability and hardware timing remain unverified; synthetic contracts cannot prove them. |
| [scripts/probe_call_audio_watch.py](../scripts/probe_call_audio_watch.py) | command, parse_wpctl_id, parse_sink_mute, is_bluetooth, graph_snapshot, props, find_gateway, call_present, sample, emit, main | all parsers and command errors; graph node/link/type/ID/property/default filters; gateway/call correlation; samples; emit; fake-clock lifecycle/change/interrupt | [test_watcher_contract](../scripts/tests/test_watcher_contract.py), [test_call_audio_watch](../scripts/tests/test_call_audio_watch.py), [test_watcher_entry](../scripts/tests/test_watcher_entry.py) | No remaining planned automated contract; native behavior on other host architectures/platforms is outside this run. |
| [scripts/probe_audio_graph.py](../scripts/probe_audio_graph.py) | valid_nodes, load_nodes | JSON root/entry/type/info/props/ID validity; boundaries; duplicate last-wins; missing/unreadable/corrupt file | [test_audio_graph](../scripts/tests/test_audio_graph.py), [test_audio_diagnostics_contract](../scripts/tests/test_audio_diagnostics_contract.py), [test_hfp_contract_extended](../scripts/tests/test_hfp_contract_extended.py) | No remaining planned automated contract; native behavior on other host architectures/platforms is outside this run. |
| [scripts/probe_obex_monitor.py](../scripts/probe_obex_monitor.py) | transfer_status, registration, message_count, main | path/framing/interface/member/status correlation; matching errors; session registration; baseline/replay/removal; CLI mode and file errors | [test_obex_monitor](../scripts/tests/test_obex_monitor.py), [test_map_events_contract](../scripts/tests/test_map_events_contract.py), [test_map_send_contract](../scripts/tests/test_map_send_contract.py) | No remaining planned automated contract; native behavior on other host architectures/platforms is outside this run. |
| [crates/nativepair-core/src/lib.rs](../crates/nativepair-core/src/lib.rs) | new, availability, set_availability, supports, platform | all platforms/capabilities/states; previous state; supports; reassignment; isolation and clone | Rust exhaustive_contract_tests | No remaining planned automated contract; native behavior on other host architectures/platforms is outside this run. |
| [crates/nativepair-cli/src/main.rs](../crates/nativepair-cli/src/main.rs) | main | no arguments; help/version aliases; unknown/extra/private arguments; exact output and exit code | [test_binary_contract](../scripts/tests/test_binary_contract.py) | No remaining planned automated contract; native behavior on other host architectures/platforms is outside this run. |
| [crates/nativepair-daemon/src/main.rs](../crates/nativepair-daemon/src/main.rs) | main | no arguments; version aliases; unknown/extra/private arguments; exact output and exit code | [test_binary_contract](../scripts/tests/test_binary_contract.py) | No remaining planned automated contract; native behavior on other host architectures/platforms is outside this run. |

The required artifacts, expected bounds, negative applicability and meaningful
interactions were inventoried before implementation. The complete inventory
contains 1363 Python methods (1346 added), and Rust has eight methods including
three added methods with 495 explicit domain rows. Pure tests use fake clocks
and command adapters. Integration fixtures execute the actual scripts with
hermetic external adapters; no subject under test is mocked.

Minimal testability changes: the shared graph normalizer exposes two pure
functions; the bus monitor parser exposes framing/correlation functions; the
watcher accepts injected command/clock/output adapters. These internal seams
have no new transport API, output schema or runtime dependency. Malformed data
now fails closed and owned resources are cleaned after cancellation. Each fix
and rationale is in the [execution record](M1_AUTOMATED_VERIFICATION.md).

Acceptance evidence: the full Python baseline (1363 methods) and Rust suite
(eight methods) passed once; the 182-scenario process stability lane passed ten
consecutive executions, including its baseline pass. Zero failures were observed.
Static checks, final native package verification and 29 assertion-level mutation
trials passed. Results are in [the execution evidence](evidence/m1-automated-execution.json). No hardware E2E is included. Remote CI is configured
but not run for these unpublished local commits.

Changed implementation areas and rollback units: capability/observer contracts;
hermetic protocol harness and parameter/discovery tests; OBEX monitor parser and
FIFO cleanup; HFP/SCO and graph normalization; audio diagnostics; packaging and
CI discovery; observer corruption guards; and the process stability runner.
Atomic commits use `test:`, `fix:` or `docs:` and each can be inspected/reverted
independently. The final handoff record lists the commit IDs.

Added fixtures/utilities live in `scripts/tests/`: `probe_harness.py`,
`fake_system.py`, `scenarios.py`, `run_suite.py`, `review_mutations.py` and
`trace_site/sitecustomize.py`. Contract families in the table are the complete
modified/added test file list. Documentation is in `docs/M1_*`, `docs/TESTING.md`,
`docs/TEST_MATRIX_M1.md` and `docs/evidence/`. Production paths are listed above;
`.github/workflows/ci.yml` discovers all contracts after building the binaries.
Generated package and raw trace/process logs remain ignored local artifacts.

Source evidence from the complete baseline is in
[`m1-automated-source-trace.json`](evidence/m1-automated-source-trace.json).
Python line/arc counts cover all three modules and embedded classifiers; Bash
DEBUG records probe/wrapper source locations. Rust and packaging fixtures are
validated by explicit contract assertions and are not instrumented in this
trace. Blank-source shell launcher events are excluded. No trace contains
arguments, graph values, identifiers or message payloads.
