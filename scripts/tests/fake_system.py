#!/usr/bin/env python3
"""Hermetic external-system adapter, never a replacement for probe logic."""
import fcntl
import json
import os
from pathlib import Path
import re
import signal
import sys

root = Path(os.environ["NATIVEPAIR_TEST_ROOT"])
config = json.loads((root / "config.json").read_text())
name = Path(sys.argv[0]).name
args = sys.argv[1:]
joined = " ".join(args)


def update(operation):
    with (root / "state.json").open("r+") as file:
        fcntl.flock(file, fcntl.LOCK_EX)
        state = json.load(file)
        result = operation(state)
        file.seek(0)
        json.dump(state, file)
        file.truncate()
        return result


def record(state):
    state["commands"].append([name, *args])
    state.setdefault("pids", {})[name + ("_monitor" if "monitor" in args else "")] = os.getpid()
    for index, rule in enumerate(config.get("routes", [])):
        if rule["command"] == name and re.search(rule.get("match", ".*"), joined):
            key = str(index)
            count = state["route_counts"].get(key, 0)
            state["route_counts"][key] = count + 1
            replies = rule.get("replies", [rule])
            reply = replies[min(count, len(replies) - 1)]
            return reply
    return None


reply = update(record)


def append_log(filename, content):
    for path in (root / "tmp").glob("*/" + filename):
        with path.open("a") as file:
            file.write(content + "\n")


if reply and reply.get("append"):
    append_log(reply["append"], reply.get("content", ""))
if reply and reply.get("kill"):
    pids = update(lambda state: state.get("pids", {}))
    for key in reply["kill"]:
        if key in pids:
            try:
                os.kill(pids[key], signal.SIGTERM)
            except ProcessLookupError:
                pass

if name == "obexctl":
    print(config.get("obex_ready", "[NEW] Client /org/bluez/obex"), flush=True)
    if config.get("obex_exit"):
        sys.exit(1)
    for line in sys.stdin:
        command = line.strip().split()
        if command and command[0] == "connect":
            target = command[-1]
            label = "MessageAccess" if target == "map" else "PhonebookAccess"
            default = ("Connection successful\nSession /org/bluez/obex/client/session0\n"
                       f"[NEW] {label} /org/bluez/obex/client/session0")
            print(config.get("obex_connect", default), flush=True)
            append_log("busctl-monitor.log", config.get("registration", ""))
            if config.get("obex_exit_after_connect"):
                sys.exit(1)
        if command and command[0] == "quit":
            break
    sys.exit(0)

if name == "busctl" and "monitor" in args:
    if reply and reply.get("exit", 0):
        sys.exit(reply["exit"])
    print(config.get("monitor_initial", "Monitoring bus message stream."), flush=True)
    (root / "monitor.ready").touch()
    signal.pause()
    sys.exit(0)

if name == "busctl" and "Dial" in args:
    update(lambda state: state.update(call_exists=True,
                                     transport=config.get("transport_on_dial", "idle")))
if name == "busctl" and "PushMessage" in args:
    payload = Path(args[args.index("PushMessage") + 2])
    update(lambda state: state.update(payload=payload.read_bytes().hex(),
                                     payload_mode=payload.stat().st_mode & 0o777))
    append_log("busctl-monitor.log", config.get("push_event", ""))

if reply is not None and not reply.get("delegate"):
    print(reply.get("stdout", ""), end="", flush=True)
    print(reply.get("stderr", ""), end="", file=sys.stderr, flush=True)
    if reply.get("signal_parent"):
        os.kill(os.getppid(), getattr(signal, reply["signal_parent"]))
    sys.exit(reply.get("exit", 0))

if name == "chmod" and config.get("capture_payload"):
    path = Path(args[-1])
    os.chmod(path, int(args[0], 8))
    update(lambda state: state.update(payload=path.read_bytes().hex(),
                                     payload_mode=path.stat().st_mode & 0o777))
    sys.exit(0)

delegated = config.get("real_tools", {})
if name in delegated:
    os.execv(delegated[name], [delegated[name], *args])

if name == "bluetoothctl":
    if args[:1] == ["info"]:
        print("Name: PRIVATE_CONTACT\n  Paired: yes\n  Trusted: yes\n  Connected: yes")
        for uuid in ("1132", "112f", "111f", "1133"):
            print(f"UUID: 0000{uuid}-0000-1000-8000-00805f9b34fb")
    elif args == ["--version"]:
        print("bluetoothctl: 5.85")
    elif args[:1] == ["connect"]:
        print("Connection successful")
    elif args == ["show"]:
        print("UUID: 00001133-0000-1000-8000-00805f9b34fb")
    elif args == ["list"]:
        print("Controller 02:00:00:00:00:01 PRIVATE_CONTACT")
    elif args in (["devices", "Paired"], ["paired-devices"]):
        print("Device 02:00:00:00:00:01 PRIVATE_CONTACT")
    else:
        sys.exit(91)
elif name == "busctl":
    clean = [arg for arg in args if arg not in ("--user", "--system")]
    if clean[0] == "list":
        print("org.bluez.obex 1 process user")
    elif clean[0] == "introspect":
        print("org.ofono.Manager GetModems\norg.ofono.VoiceCallManager GetCalls")
        print("org.pipewire.Telephony.AudioGateway1 Dial HangupAll SendTones")
        print("org.pipewire.Telephony.AudioGatewayTransport1 Activate")
    elif clean[0] == "get-property":
        prop = clean[4]
        if prop == "State":
            transport = update(lambda state: state["transport"])
            print('s "active"' if "/call" in clean[2] else f's "{transport}"')
        elif prop == "Codec":
            print("y 2")
        elif prop == "RejectSCO":
            print("b false")
        elif prop == "Target":
            print('s "00001132-0000-1000-8000-00805f9b34fb"')
        elif prop == "SupportedTypes":
            print('as 1 "SMS_GSM"')
        else:
            sys.exit(92)
    elif clean[0] == "call":
        method = clean[4]
        if method == "GetModems":
            print('a(oa{sv}) 1 "/org/pipewire/Telephony/ag0" 0')
        elif method == "GetCalls":
            if update(lambda state: state["call_exists"]):
                print(config.get("active_calls", 'a(oa{sv}) 1 "/org/pipewire/Telephony/ag0/call0" 1 "State" s "active"'))
            else:
                print("a(oa{sv}) 0")
        elif method == "HangupAll":
            update(lambda state: state.update(call_exists=False))
        elif method == "Activate":
            update(lambda state: state.update(transport="active"))
        elif method == "PushMessage":
            print('oa{sv} "/org/bluez/obex/client/session0/transfer0" 0')
        elif method in ("ListFolders", "ListMessages", "List"):
            print({'ListFolders': 'aa{sv}', 'ListMessages': 'a{oa{sv}}', 'List': 'a(ss)'}[method] + ' 1 "PRIVATE_CONTACT" s "+15551234567"')
        elif method == "GetSize":
            print("q 1")
        elif method not in ("Dial", "Select", "SetFolder"):
            sys.exit(93)
    else:
        sys.exit(94)
elif name == "pw-dump":
    print(json.dumps([{"id": identifier, "type": "PipeWire:Interface:Node",
                       "info": {"state": "running", "props": {
                           "api.bluez5.address": "02:00:00:00:00:01",
                           "api.bluez5.profile": "headset-head-unit",
                           "media.class": role}}}
                      for identifier, role in [(41, "Audio/Sink"), (42, "Audio/Source")]]))
elif name == "wpctl":
    print("id 41, type Node" if "SINK" in args[-1] else "id 42, type Node")
elif name == "pw-top":
    print("S   ID  QUANT RATE WAIT BUSY W/Q B/Q ERR FORMAT NAME")
    print("R 41 256 48000 0 0 0 0 1 PRIVATE_CONTACT")
    print("S   ID  QUANT RATE WAIT BUSY W/Q B/Q ERR FORMAT NAME")
    print("R 41 256 48000 0 0 0 0 2 PRIVATE_CONTACT")
elif name in ("systemctl", "journalctl"):
    pass
elif name in ("pipewire", "wireplumber"):
    print(name + " 1.6.0")
elif name == "sdptool":
    print('<attribute id="0x0315"/><attribute id="0x0316"/><attribute id="0x0317"/><uuid value="0x1132"/>')
elif name == "dpkg-query":
    print("5.85-1")
elif name == "pgrep":
    if config.get("obex_pid"):
        print(config["obex_pid"])
    else:
        sys.exit(1)
elif name == "strings":
    print(config.get("strings", "x-bt/MAP-NotificationRegistration\nx-bt/MAP-event-report\nMessage Notification server"))
elif name == "sleep":
    pass
else:
    sys.exit(95)
