# Protocol Feasibility

## Status

Milestone M1 is in progress.

The purpose of M1 is to prove what a real modern phone exposes to Linux before product behavior is built around it. Profile advertisement is evidence for further probing, not proof that a feature works.

## Reference path

The Linux host is expected to use the system Bluetooth stack:

```text
Phone
  |
  +-- Bluetooth Classic --> BlueZ --> obexd --> MAP / PBAP
  |
  +-- Bluetooth Classic --> BlueZ --> HFP control/audio stack
  |
  +-- Bluetooth LE -------> BlueZ --> ANCS (iPhone only)
```

NativePair must not replace BlueZ or bypass the operating-system pairing/trust model.

## Local device variable

During manual feasibility work, keep the phone address in the shell environment instead of repeating it in commands or pasted logs:

```bash
export NATIVEPAIR_DEVICE='AA:BB:CC:DD:EE:FF'
```

NativePair probe scripts accept this variable as the default device. An explicit `--device` argument overrides it. Remove it when finished:

```bash
unset NATIVEPAIR_DEVICE
```

The scripts must never echo the address.

## Phase-0 host probe

`scripts/probe-bluetooth.sh` is the first reproducible diagnostic. It reports only bounded capability/environment facts and intentionally suppresses phone names, Bluetooth addresses, message content, contacts, and other personal data.

Without `NATIVEPAIR_DEVICE` or a device argument it checks:

- BlueZ tool availability and version;
- whether the Bluetooth service is active;
- whether an adapter is visible;
- whether OBEX tooling is installed;
- whether a session D-Bus is available;
- whether a user `mpris-proxy` service is active when systemd user services are available.

With `NATIVEPAIR_DEVICE` or `--device <Bluetooth address>` it additionally checks pairing/trust/connection flags and whether the remote device advertises UUIDs associated with:

- MAP Message Access Server: `00001132-0000-1000-8000-00805f9b34fb`;
- PBAP Phonebook Access Server: `0000112f-0000-1000-8000-00805f9b34fb`;
- HFP Audio Gateway: `0000111f-0000-1000-8000-00805f9b34fb`;
- Apple Notification Center Service: `7905f431-b5ce-4e99-a40f-4b1e122d00d0`.

These UUID checks are hints only. A capability remains `unknown` until an end-to-end operation succeeds.

## OBEX session probe

`scripts/probe-obex-session.sh` creates a temporary MAP or PBAP session through `org.bluez.obex.Client1.CreateSession`, inspects the resulting session, and removes it on exit.

The probe records:

- whether `org.bluez.obex` is available;
- whether the device is paired;
- whether `CreateSession` succeeds;
- the non-sensitive target service UUID reported by `org.bluez.obex.Session1`;
- the set of interfaces exported on the session object;
- whether the expected MAP/PBAP interface is present.

The session path and Bluetooth address are intentionally not printed.

## OBEX read probe

`scripts/probe-obex-read.sh` performs the first bounded level-4 checks while keeping the same privacy boundary.

For MAP it:

- lists the current folder with a bounded result count;
- selects `telecom/msg`;
- requests at most one inbox entry;
- asks only for the message `type` field;
- reports only whether the calls succeeded and whether the returned arrays were empty.

For PBAP it:

- selects the internal phonebook;
- queries whether the phonebook is non-empty without printing its exact size;
- requests at most one contact-list entry;
- suppresses the raw response and reports only success/non-empty state.

Raw D-Bus responses exist only in a temporary directory and are deleted on exit. They are never printed by the probe.

Usage:

```bash
./scripts/probe-obex-read.sh --target map
./scripts/probe-obex-read.sh --target pbap
```

## MAP event probe

BlueZ 5.85 automatically attempts MAP Notification Registration when its MAP client driver creates the `MessageAccess1` session interface. NativePair therefore does not need a separate public D-Bus registration call for this feasibility test.

Before interpreting an event timeout, run `scripts/probe-mns.sh`. It verifies whether the local BlueZ/obexd installation appears capable of receiving MAP event callbacks through the Message Notification Server (MNS, UUID `00001133-0000-1000-8000-00805f9b34fb`). The probe checks the running obexd process, whether MNS was explicitly disabled, whether the MNS plugin appears compiled into obexd, controller UUID visibility, and the local SDP record when `sdptool` is available.

For Android event tests, the trigger must be a real SMS/MMS rather than an RCS chat. Google Messages can deliver RCS over Wi-Fi/mobile data, while SMS/MMS use the carrier path. The event probe is therefore inconclusive if the message transport was not confirmed.

### BlueZ 5.85 server-profile registration defect

Upstream BlueZ issue #2315 documents a 5.85 startup-order defect that can leave all obexd server profiles unregistered when `org.bluez` is already present before `obex_server_init()` populates the profile list. The affected environment in that report is Ubuntu 26.04.

A matching NativePair diagnostic pattern is:

- MAP client signature present in `obexd`;
- MNS server signature present in `obexd`;
- MNS not explicitly disabled;
- MNS controller UUID absent.

For controlled feasibility testing only, the upstream workaround is:

```bash
sudo systemctl restart bluetooth
```

Run it only after `obexd` is already running, then rerun `scripts/probe-mns.sh`. This interrupts active Bluetooth connections and is not a NativePair product requirement.

If MNS is present but MAP notification registration is still not observed, run:

```bash
./scripts/probe-map-sdp.sh
```

BlueZ 5.85 only queues `x-bt/MAP-NotificationRegistration` when the remote MAP MAS SDP record exposes `MASInstanceID` (attribute `0x0315`). The probe reports only attribute presence and suppresses the raw SDP record.

`scripts/probe-map-events.sh` starts a low-level session-bus monitor before creating the MAP session. It uses that temporary monitor stream to catch the short-lived internal `org.bluez.obex.Transfer1` used for notification registration, then keeps the MAP session alive for a bounded window and watches for a new `org.bluez.obex.Message1` object. It does not inspect message properties.

Raw monitor output can contain session metadata, so it is stored only in a temporary directory and deleted on exit. The probe prints only bounded status fields.

Run the probe, then arrange for one incoming SMS during the wait window:

```bash
./scripts/probe-map-events.sh
```

The default window is 60 seconds. Override it without changing the script:

```bash
NATIVEPAIR_EVENT_TIMEOUT=90 ./scripts/probe-map-events.sh
```

No incoming message during the window produces an inconclusive result, not a failure.

## MAP send probe

`scripts/probe-map-send.sh` characterizes one outgoing SMS through BlueZ MAP `PushMessage`.

The probe uses a fixed ASCII test body and requires the recipient through `NATIVEPAIR_SMS_RECIPIENT` in E.164 form. The phone number and bMessage payload are never printed or committed. The generated bMessage exists only in a mode-0600 temporary file and is deleted on exit.

Default invocation is preflight only and cannot send:

```bash
./scripts/probe-map-send.sh
```

A real send requires an explicit side-effect flag:

```bash
./scripts/probe-map-send.sh --send
```

The probe selects `telecom/msg`, pushes to `outbox`, uses UTF-8, sets `Transparent=true`, and disables MAP retry to reduce duplicate-send risk. It writes the bMessage body directly with CRLF framing and validates the generated structure before any real send. A successful OBEX transfer proves that the remote accepted the pushed message; the human test must also verify that the intended recipient received exactly one SMS before level 5 send support is recorded.

The first send attempt from the initial probe revision is excluded from capability evidence because Bash command substitution stripped the LF from the final CRLF of the `END:MSG` line, producing malformed bMessage framing.

## HFP call-control preflight

`scripts/probe-hfp.sh` characterizes the native no-companion HFP path without placing or modifying a call.

The intended Linux role is HFP Hands-Free while the phone remains the HFP Audio Gateway. The probe verifies the phone's HFP AG advertisement, connects to the phone's remote HFP Audio Gateway service (UUID `0000111f-0000-1000-8000-00805f9b34fb`), and then inspects PipeWire's native Bluetooth Telephony service on the user D-Bus. BlueZ profile selection names the remote service: targeting remote `hfp-hf` would reverse the roles and is incorrect for a phone acting as Audio Gateway.

A successful preflight requires a PipeWire Telephony AudioGateway object for the phone. That object is treated as evidence that the HFP service-level connection reached PipeWire's native HFP backend. The probe also verifies that the call-control API exposes `Dial`, `HangupAll`, `SendTones`, and call-state query support, but it does not invoke any mutating call-control method.

The probe suppresses raw D-Bus replies because modem and call objects can carry phone numbers or caller metadata. Only boolean capability results are printed.

Run:

```bash
./scripts/probe-hfp.sh
```

This preflight can establish the HFP profile connection, but it never creates, answers, rejects, hangs up, or otherwise modifies a phone call. Actual call-control and SCO audio tests require separate explicit approval and dedicated probes.

## HFP call-control mutation probe

`scripts/probe-hfp-call.sh` is a guarded call-control probe layered on top of the proven HFP service-level connection.

Default invocation is preflight only. It connects to the remote HFP Audio Gateway, resolves the PipeWire Telephony AudioGateway object, verifies the call-control API, and checks that no call object already exists. It never prints a destination number.

A real call requires both a private `NATIVEPAIR_CALL_RECIPIENT` value and the explicit `--dial` flag. The probe refuses to dial while any call object already exists. After an accepted `Dial`, it waits briefly for a PipeWire Telephony call object and then invokes `HangupAll`.

Because `--dial` creates a real telephone call and may incur carrier charges, it must only be used as a separately approved side-effect test.

## HFP SCO audio characterization plan

HFP audio feasibility is split into two explicit stages so that transport discovery is separated from real-call side effects.

### Stage A: transport preflight

`scripts/probe-hfp-audio.sh` must:

- connect only to the phone's remote HFP Audio Gateway service;
- resolve the existing PipeWire Telephony AudioGateway object;
- verify `org.pipewire.Telephony.AudioGatewayTransport1`;
- read the transport `State`, `Codec`, and `RejectSCO` properties;
- verify that the `Activate` method is exposed;
- print only bounded, privacy-safe status fields;
- never invoke `Activate`, never place a call, and never open an audio stream.

The preflight is successful when the Telephony AudioGateway transport interface is present and its properties can be read. An idle transport before a call is expected and is not a failure. `RejectSCO=true` is recorded as a blocker for the later SCO test rather than silently changed.

### Stage B: real-call SCO proof

The later real audio test requires separate explicit approval because it creates a telephone call. It must:

- refuse to proceed if a pre-existing call exists;
- use the already approved PipeWire Telephony HFP path;
- create one guarded outgoing test call;
- observe a call object;
- wait until that call's `org.pipewire.Telephony.Call1.State` becomes `active`, which requires the remote party to answer;
- request transport activation only after the call is active;
- observe the transport reaching `active`;
- verify that PipeWire exposes the HFP/SCO audio endpoints;
- terminate the call on success, error, or interruption;
- never print the destination number, caller metadata, or captured voice payload.

The first real SCO attempt is excluded from audio capability evidence. That probe invoked `AudioGatewayTransport1.Activate` immediately after a call object appeared, while the outgoing call could still be in `dialing` or `alerting`. The activation request failed. The corrected probe must condition-wait for `Call1.State=active` before requesting SCO activation.

### Second real SCO attempt

The second real attempt successfully dialed and observed a call object, but the probe reported `call_state_before_activate=unknown` and timed out before invoking `Activate`.

Human observation during that real call was asymmetric: the remote party could hear the local user, while the local user could not hear the remote party. This is diagnostic evidence only, not bidirectional SCO proof.

The probe bug is that it cached the first call object path and queried that path repeatedly. PipeWire may remove/recreate or otherwise change the current call object while the outgoing call progresses. The corrected state wait must refresh `GetCalls` on every poll and derive the current state from the fresh snapshot, with a bounded fallback property read.

Before changing routing, the probe must also report whether the current default PipeWire sink/source correspond to the HFP nodes. Routing inspection is read-only; no default device or link is changed by this diagnostic stage.

Transport activation alone is not sufficient evidence for bidirectional audio. Final SCO audio support requires both system-level evidence that the transport/endpoints are active and human confirmation that audio is usable in both directions.

Rollback point: the Stage A probe is additive and can be removed independently without changing production behavior or the already-proven HFP call-control path.

### Audio health probe interpretation

The first `probe-audio-health.sh` revision reports aggregate `pw-top` ERR growth. That signal is intentionally diagnostic, not a pass/fail criterion: a node can accumulate PipeWire xruns/errors without producing an audible regression on the current playback path.

Before using ERR growth as evidence for HFP-induced playback degradation, the probe must classify the affected node without printing names or personal metadata. At minimum it must report whether growth occurred on:

- the current default audio sink;
- the current default audio source;
- any BlueZ node;
- any HFP/SCO node;
- any output-audio application stream;
- a running node versus an inactive/suspended node.

This keeps the diagnostic bounded while separating actual playback-path impact from unrelated graph noise.

## Known BlueZ mpris-proxy interference

On the Ubuntu 26.04 reference host, BlueZ 5.85-4ubuntu0.2 produced an `mpris-proxy` SIGSEGV while MAP feasibility testing was active.

This is tracked as an environment/tooling defect, not a NativePair protocol result. Upstream BlueZ has a known null-dereference fix in `mpris-proxy` around OBEX property handling. Until the distro package carries the fix, manual MAP/PBAP feasibility runs may temporarily stop `mpris-proxy.service` to remove unrelated media-proxy noise from the experiment.

NativePair must not require disabling `mpris-proxy` as a product behavior. This is only a controlled feasibility workaround.

## Evidence ladder

A capability progresses through these evidence levels:

1. **Host ready**: required Linux service/tooling exists.
2. **Advertised**: the phone advertises the expected service/profile.
3. **Session established**: Linux creates the relevant protocol session and the expected target interface is available.
4. **Read path proven**: bounded synthetic or user-approved data can be listed/fetched.
5. **Write/event path proven**: send/update/event behavior works where applicable.
6. **Recovery proven**: disconnect/reconnect, permission denial, service restart, and stale-session behavior are characterized.

NativePair documentation must distinguish these levels. A lower level must never be presented as product support.

## Android reference target

The first Android reference device is a modern Pixel. Required experiments:

- pair/trust through normal BlueZ UX;
- inspect MAP/PBAP/HFP advertisement;
- create MAP session through obexd;
- list MAP folders/messages without persisting content;
- characterize message send behavior;
- characterize MAP notification/event behavior;
- create PBAP session and list contact metadata without committing personal fixtures;
- characterize HFP call-control feasibility.

The known risk is that a profile may be advertised and a session may be accepted while message listing still returns no usable data. NativePair must model that as a failed/limited capability probe, not as support.

## iPhone reference target

When iPhone hardware is available:

- repeat MAP/PBAP/HFP experiments;
- probe ANCS over BLE;
- document the iOS Bluetooth permission/settings required for each profile;
- characterize behavior when the phone is locked and notification previews are restricted.

## Privacy rules for feasibility work

Never commit:

- real Bluetooth addresses;
- real phone names;
- message bodies;
- phone numbers;
- contact names;
- call history;
- notification bodies.

If protocol payload fixtures are needed, create synthetic equivalents after the real behavior is understood.

## Exit criteria for M1

M1 is complete only when the repository contains a capability matrix backed by reproducible evidence for at least one modern Android device and, where hardware is available, one current iPhone. Failed capabilities are valid results and must be recorded explicitly.
