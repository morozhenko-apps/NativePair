#!/usr/bin/env python3
"""Read a captured busctl stream and emit only a correlated transfer status."""
import re
import sys

TRANSFER = re.compile(r"/org/bluez/obex/client/session[0-9]+/transfer[0-9]+")


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


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 2:
        print("unknown")
        return 2
    try:
        with open(args[0], encoding="utf-8", errors="replace") as handle:
            text = handle.read()
    except OSError:
        print("unknown")
        return 1
    print(transfer_status(text, args[1]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
