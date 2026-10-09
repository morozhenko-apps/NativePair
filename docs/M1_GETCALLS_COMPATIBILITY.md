# GetCalls wire compatibility correction

Date: 2026-10-09. Mode: B — regression verification and exposed-defect fix.

## Analysis and evidence

The selected Pixel 6a (Android 17) is correlated with its paired BlueZ device
using local addresses in memory. Bluetooth is enabled; HFP transport preflight
succeeds with State=idle and RejectSCO=false. No-dial SCO preflight fails because
the actual GetCalls reply is `a{oa{sv}} 0`, whereas current guards and default
test adapters expect `a(oa{sv}) 0`. Live introspection declares GetCalls output
`a{oa{sv}}`. The method succeeds and returns zero calls. This is an adapter
contract defect, not a Bluetooth connection or phone permission failure.

Upstream reference: [PipeWire Telephony service](https://github.com/PipeWire/pipewire/blob/master/spa/plugins/bluez5/README-Telephony.md).
GetCalls is implemented on org.ofono.VoiceCallManager for compatibility. The
local introspection and sanitized wire shape establish the installed contract.

## Scope and decision

Accept the actual dictionary signature and retain the existing array-of-struct
form for compatibility. Empty-call guards still require exactly zero and no
object payload. Invalid/unknown data must never authorize Dial. No new API,
model, security boundary, routing policy or dependency is introduced. Correct
the existing Bash call/SCO guards and passive Bash/Python observer signatures.
Use the real dictionary form in default GetCalls fakes; keep explicit tests
for both signatures. GetModems is a different method and remains unchanged.

## Inventory, branch and interaction matrix

All affected artifacts are listed below. Every row specifies planned assertions;
no new tests precede this inventory. Existing full matrices remain applicable.

| Artifact | Branches and interactions | Planned scenarios | Category |
| --- | --- | ---: | --- |
| call/SCO empty guard | 2 probes × 2 signatures × plain/trailing-whitespace empty; exact no-dial preflight and zero Dial/HangupAll/Activate | 8 | Positive |
| call/SCO existing guard | 2 probes × 2 signatures; exact blocked state and no mutations | 4 | N7 |
| call/SCO owned-call lifecycle | 2 probes × 2 signatures; empty before Dial and active after; exactly one Dial/HangupAll, expected Activate count | 4 | Positive |
| call/SCO malformed empty guard | 2 probes × 2 signatures × counts 00, 01, -1, overflow, absent, garbage; rejection and zero mutations | 24 | N6 |
| passive HFP and watcher | 2 consumers × 2 signatures × zero, zero whitespace, one selected-gateway call; exact no/no/yes | 12 | Positive |
| passive HFP and watcher | 2 consumers × 2 signatures × count without object, foreign gateway, zero with object, 01, overflow, suffix path, negative, private malformed text; exact unknown | 32 | N6 |
| **Total** | Every planned combination is explicit | **84** | Positive 24; N6 56; N7 4 |

N1/N2 numeric/type boundaries use the N6 primary category here because the
input is an external wire reply. N3 command failures, N4 idempotency, N5 state
transitions, N9 cancellation, N10 privacy and N12 cleanup retain their existing
tests; new shell cases additionally assert privacy/cleanup and mutation counts.
N8 and N11 have no new date/billing behavior. No hardware E2E is added.

## Plan, verification and rollback

1. Add all 84 regression rows and confirm actual dictionary cases fail before
   the production fix. Existing production functions are the subject; only
   external command adapters are replaced.
2. Apply the four signature compatibility changes and change default GetCalls
   fixtures to the observed form. Preserve asserts and no-call ownership rules.
3. Run new rows, complete Python suite once, syntax/compilation checks once,
   and targeted mutation review (dictionary acceptance removed / malformed
   reply treated as empty). Repeat no-dial Pixel preflight after success.
   No ten-run static/pure rerun; process ownership/signal logic is unchanged.
4. Update canonical inventory, counts, source maps and sanitized device evidence.
   Keep previous stability evidence tied to its tested commit, not silently
   rebrand it as ten runs of new source. Commit the scoped fix and records.

Risk: accepting a second wire form must not make malformed empty replies valid.
Explicit canonical-zero assertions and mutation review protect that boundary.
Rollback: revert the scoped compatibility commit; no pairing/routing changes
or live calls are performed. The earlier automated completion reflects its
inventoried synthetic contracts; hardware revealed their missing wire form.

## State

Inventory and plan were committed before regression implementation (d7ee7de).
All 84 rows were added. Before the fix, 12 failed in 18.624 seconds; after the
four production signature corrections, all 84 passed in 22.021 seconds. Default
GetCalls fixtures now use the actual dictionary form. Six targeted mutations
check removal of dictionary support in each consumer and acceptance of 00 in
each dial guard. All six targeted mutations were killed by assertion failures; each unmodified
selection passed first. The complete 1447-method Python suite passed once in
270.605 seconds with no failures. Shell syntax and Python compilation passed.
The native amd64 Debian package was rebuilt and verified. Rust sources did
not change, so the previously successful Rust quality gate was not repeated.

The actual Pixel no-dial SCO, passive HFP and read-only routing probes all
passed after the fix. GetCalls is readable and confirms no existing call;
transport is idle, RejectSCO is false, and Activate is available. No HFP nodes
exist while idle. No call/Activate/audio stream or routing mutation occurred.
All owned terminal/process sessions completed and closed (Terminal closed).
The test recipient is not configured. Next action requires explicit live-call
authorization, a dedicated destination and human readiness.

The initial preparation wrapper accidentally omitted its target environment
when spawning probes; all three rejected their arguments with exit 2 before
Bluetooth operations. That wrapper was corrected and rerun; those setup exits
are not classified as phone failures or flaky tests.
No live call is
authorized. Final hardware gate still requires an approved destination and
human confirmation of the actual computer speaker/headphones and microphone.
