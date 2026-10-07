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
Evidence date: 2026-10-06

| Capability | Native mechanism | Highest proven level | Result | Notes |
| --- | --- | ---: | --- | --- |
| Messages read/list | MAP | 4 | Proven | Session, folders, `telecom/msg`, and non-empty inbox listing all succeeded. Personal payloads were suppressed. |
| Messages send | MAP | 5 | Proven | Corrected bMessage passed local structure validation, PushMessage returned a transfer, the transfer reached complete, and the intended recipient confirmed exactly one SMS with the expected fixed probe text. |
| Message events | MAP | 5 | Proven | A real incoming SMS produced a new Message1 object through the MAP/MNS path. Registration Transfer1 was observed; explicit completion status was not captured, but end-to-end event delivery proves registration was effective. |
| Contacts | PBAP | 4 | Proven | Internal phonebook select, size query, and non-empty bounded listing succeeded. Personal payloads were suppressed. |
| Calls | HFP (phone AG, Linux HF) | 5 | Call control proven; SCO preflight ready | Dial and HangupAll are proven. AudioGatewayTransport1 is present, mSBC is negotiated, and RejectSCO=false. Real SCO activation and bidirectional audio remain unproven. |
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
- contact listing through PBAP.

The next unknowns are active behavior rather than basic accessibility:



- HFP audio routing;
- reconnect/recovery behavior.
