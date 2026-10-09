# Capability Matrix

This matrix records observed capability evidence, not platform promises.

Evidence levels:

1. host ready;
2. profile advertised;
3. protocol session established;
4. bounded read path proven;
5. write/event path proven;
6. recovery behavior characterized.

## Android reference device

Reference device: Pixel 6a  
Host: Ubuntu 26.04  
BlueZ: 5.85 / Ubuntu package 5.85-4ubuntu0.2  
Initial evidence date: 2026-10-06; HFP audio update: 2026-10-09 (Pixel Android 17).

| Capability | Native mechanism | Highest proven level | Result | Notes |
| --- | --- | ---: | --- | --- |
| Messages read/list | MAP | 4 | Proven | Session, folders, `telecom/msg`, and non-empty inbox listing all succeeded. Personal payloads were suppressed. |
| Messages send | MAP | 5 | Proven | Corrected bMessage passed local structure validation, PushMessage returned a transfer, the transfer reached complete, and the intended recipient confirmed exactly one SMS with the expected fixed probe text. |
| Message events | MAP | 5 | Proven | A real incoming SMS produced a new Message1 object through the MAP/MNS path. Registration Transfer1 was observed; explicit completion status was not captured, but end-to-end event delivery proves registration was effective. |
| Contacts | PBAP | 4 | Proven | Internal phonebook select, size query, and non-empty bounded listing succeeded. Personal payloads were suppressed. |
| Calls | HFP (phone AG, Linux HF) | 5 | Call control proven; computer duplex human-confirmed | One authorized 2026-10-09 call reached active; SCO was already active, so no Activate call was required. The user explicitly confirmed sound and microphone in both directions through the computer. The probe nevertheless found zero matching HFP nodes and exited with hfp_nodes_not_ready; endpoint enumeration remains unresolved. Owned-call cleanup succeeded and post-call GetCalls was empty with transport idle. See [live result](M1_HFP_AUDIO_NEXT.md). This establishes feasibility for the observed setup, not repeatability, recovery or a successful automated audio gate. |
| App notifications | Generic Android Bluetooth | — | No baseline mechanism selected | Android has no project-approved generic equivalent to iPhone ANCS for arbitrary app notifications. |
| Apple notifications | ANCS | — | Not applicable | ANCS was not advertised by the Android reference device, as expected. |

## Environment observations

The Ubuntu BlueZ `mpris-proxy` process crashed during an early MAP attempt. The crash is treated as a distro/BlueZ environment issue and is not counted against MAP/PBAP capability evidence.

The host also reproduced upstream BlueZ issue #2315: server-side OBEX profiles including MNS were absent until `bluetoothd` was restarted while `obexd` remained running. After the restart, MNS and Object Push UUIDs became visible. This is recorded as a BlueZ 5.85 / Ubuntu 26.04 compatibility defect, not a Pixel limitation.

A short-lived Bluetooth access/authorization UI appeared on the phone during later probing. The bounded read operations completed successfully.

## Interpretation

For the Pixel 6a, NativePair's no-companion-app Android foundation is currently proven for:

- SMS/message listing through MAP;
- outgoing SMS through MAP;
- incoming MAP message events;
- contact listing through PBAP;
- HFP call control and one human-confirmed bidirectional call through the computer.

Remaining gaps include:

- automated HFP endpoint enumeration and graph-level route evidence;
- repeatable call/audio lifecycle across reconnects;
- reconnect/recovery behavior.
