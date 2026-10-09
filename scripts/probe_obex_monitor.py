#!/usr/bin/env python3
"""Read a captured busctl stream and emit only a correlated transfer status."""
import re
import sys

TRANSFER = re.compile(r"/org/bluez/obex/client/session[0-9]+/transfer[0-9]+")
SESSION = re.compile(r"/org/bluez/obex/client/session[0-9]+")


def transfer_status(text, path):
    """An unrelated, malformed or incomplete status is never send evidence."""
    if not TRANSFER.fullmatch(path):
        return "unknown"
    complete = False
    for block in re.split(r"(?m)^\s*(?=(?:‣\s*)?Type=)", text):
        if not re.search(r"\bType=signal\b", block):
            continue
        if not re.search(r"\bPath=" + re.escape(path) + r"(?=\s|$)", block):
            continue
        if not re.search(r"\bInterface=org\.freedesktop\.DBus\.Properties(?=\s|$)", block):
            continue
        if not re.search(r"\bMember=PropertiesChanged(?=\s|$)", block):
            continue
        if not re.search(r'STRING "org\.bluez\.obex\.Transfer1";', block):
            continue
        statuses = re.findall(r'STRING "Status";\s+VARIANT "s" \{\s+STRING "(complete|error)";', block)
        if "error" in statuses:
            return "error"
        complete |= "complete" in statuses
    return "complete" if complete else "unknown"


def registration(text, session):
    """Return registration transfer presence/status for this owned session."""
    if not SESSION.fullmatch(session):
        return "no not_seen"
    paths = set()
    for block in re.split(r"(?m)^\s*(?=(?:‣\s*)?Type=)", text):
        if not re.search(r"\bType=signal\b", block):
            continue
        changed = (re.search(r"\bInterface=org\.freedesktop\.DBus\.Properties(?=\s|$)", block)
                   and re.search(r"\bMember=PropertiesChanged(?=\s|$)", block))
        added = (re.search(r"\bInterface=org\.freedesktop\.DBus\.ObjectManager(?=\s|$)", block)
                 and re.search(r"\bMember=InterfacesAdded(?=\s|$)", block))
        if not (changed or added):
            continue
        if 'STRING "org.bluez.obex.Transfer1";' not in block:
            continue
        paths.update(re.findall(re.escape(session) + r"/transfer[0-9]+(?=[\s\"]|$)", block))
    if not paths:
        return "no not_seen"
    statuses = {transfer_status(text, path) for path in paths}
    return "yes " + ("error" if "error" in statuses else "complete" if "complete" in statuses else "unknown")


def message_count(text, session, obexctl=False):
    """Count unique additions, permitting a new generation after removal."""
    if not SESSION.fullmatch(session):
        return 0
    active = set()
    count = 0
    pattern = re.escape(session) + r"/message[0-9]+"
    if obexctl:
        events = re.findall(r"\[(NEW|DEL)\][^\n]*?Message (" + pattern + r")(?=\s|$)", text)
    else:
        events = []
        for block in re.split(r"(?m)^\s*(?=(?:‣\s*)?Type=)", text):
            if not re.search(r"\bType=signal\b", block) or 'STRING "org.bluez.obex.Message1";' not in block:
                continue
            if not re.search(r"\bInterface=org\.freedesktop\.DBus\.ObjectManager(?=\s|$)", block):
                continue
            member = re.search(r"\bMember=Interfaces(Added|Removed)(?=\s|$)", block)
            if not member:
                continue
            for path in re.findall(r'OBJECT_PATH "(' + pattern + r')";', block):
                events.append(("NEW" if member[1] == "Added" else "DEL", path))
    for kind, path in events:
        if kind == "DEL":
            active.discard(path)
        elif path not in active:
            active.add(path)
            count += 1
    return count


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    mode = "transfer"
    if args and args[0] in ("--messages", "--obex-messages", "--registration"):
        mode, *args = args
    if len(args) != 2:
        print("unknown")
        return 2
    try:
        with open(args[0], encoding="utf-8", errors="replace") as handle:
            text = handle.read()
    except OSError:
        print("unknown")
        return 1
    if mode == "--registration":
        print(registration(text, args[1]))
    elif mode in ("--messages", "--obex-messages"):
        print(message_count(text, args[1], obexctl=mode == "--obex-messages"))
    else:
        print(transfer_status(text, args[1]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
