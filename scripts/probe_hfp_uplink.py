#!/usr/bin/env python3
"""One-shot, read-only HFP uplink graph observation without personal output."""

import json
import os
import re
import shutil
import sys

from probe_audio_graph import hfp_direction, valid_nodes
from probe_call_audio_watch import command, parse_sink_mute, parse_wpctl_id


def _valid_target(target):
    return isinstance(target, str) and re.fullmatch(
        r"(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}", target) is not None


def snapshot(objects, source_id, target):
    """Count distinct directly linked sources; never infer audible signal."""
    if not _valid_target(target):
        return None
    try:
        nodes = {node["id"]: node["info"] for node in valid_nodes(objects)}
    except ValueError:
        return None
    sources = {nid: info for nid, info in nodes.items()
               if info["props"].get("media.class") == "Audio/Source"}
    uplinks = set()
    for nid, info in nodes.items():
        props = info["props"]
        address = props.get("api.bluez5.address")
        if (isinstance(address, str) and address.casefold() == target.casefold()
                and hfp_direction(props) == "sink"):
            uplinks.add(nid)
    connected = set()
    for obj in objects:
        if not isinstance(obj, dict) or obj.get("type") != "PipeWire:Interface:Link":
            continue
        info = obj.get("info")
        if not isinstance(info, dict) or info.get("state") != "active":
            continue
        origin, destination = info.get("output-node-id"), info.get("input-node-id")
        if (type(origin) is int and type(destination) is int
                and origin in sources and destination in uplinks):
            connected.add(origin)
    default = sources.get(source_id) if type(source_id) is int else None
    state = default.get("state") if default is not None else None
    if state not in ("running", "idle", "suspended", "error"):
        state = "unknown"
    return {
        "target_uplink_endpoints": len(uplinks),
        "active_direct_sources": len(connected),
        "active_direct_alsa_sources": sum(
            sources[nid]["props"].get("device.api") == "alsa" for nid in connected),
        "default_source_present": "yes" if default is not None else "no",
        "default_source_is_alsa": (
            "yes" if default["props"].get("device.api") == "alsa" else "no"
        ) if default is not None else "unknown",
        "default_source_state": state,
        "default_source_directly_linked": (
            "yes" if source_id in connected else "no"
        ) if default is not None else "unknown",
    }


def sample(target):
    """Use bounded captured reads; raw graph, addresses and IDs stay in memory."""
    if not _valid_target(target):
        return None
    raw = command(["pw-dump"])
    if raw is None:
        return None
    try:
        objects = json.loads(raw)
    except json.JSONDecodeError:
        return None
    source = parse_wpctl_id(command(["wpctl", "inspect", "@DEFAULT_AUDIO_SOURCE@"]))
    result = snapshot(objects, source, target)
    if result is None:
        return None
    result["default_source_muted"] = parse_sink_mute(command(
        ["wpctl", "get-volume", "@DEFAULT_AUDIO_SOURCE@"]))
    return result


def main():
    args = sys.argv[1:]
    if args in (["--help"], ["-h"]):
        print(__doc__)
        print("Usage: NATIVEPAIR_DEVICE=<paired address> python3 scripts/probe_hfp_uplink.py")
        return 0
    if args:
        print("probe_error=arguments_not_supported")
        return 2
    target = os.environ.get("NATIVEPAIR_DEVICE")
    if not _valid_target(target):
        print("probe_error=invalid_or_missing_target")
        return 2
    if not all(shutil.which(tool) for tool in ("pw-dump", "wpctl")):
        print("probe_error=read_only_tool_missing")
        return 1
    print("nativepair_hfp_uplink_schema=1")
    print("personal_payload_printed=no")
    print("audio_configuration_changed=no")
    print("call_performed=no")
    try:
        result = sample(target)
    except KeyboardInterrupt:
        print("probe_complete=interrupted")
        return 130
    if result is None:
        print("probe_error=graph_snapshot_unavailable")
        print("probe_complete=no")
        return 1
    for name, value in result.items():
        print(f"{name}={value}")
    print("note=direct_graph_links_only_not_physical_microphone_or_voice_proof")
    print("probe_complete=yes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
