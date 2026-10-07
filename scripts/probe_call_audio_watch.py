#!/usr/bin/env python3
"""Passive, privacy-safe PipeWire call-audio observer. Never modifies audio."""

import argparse
import json
import re
import shutil
import subprocess
import time

TELEPHONY = "org.pipewire.Telephony"
CALL_PATH = re.compile(r"/org/pipewire/Telephony/ag[0-9]+/call[0-9]+")
AG_PATH = re.compile(r"/org/pipewire/Telephony/ag[0-9]+")


def command(args):
    """Captured, bounded, read-only commands. Never forward output/stderr."""
    try:
        result = subprocess.run(args, capture_output=True, text=True,
                                timeout=4, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return result.stdout if result.returncode == 0 else None


def parse_wpctl_id(output):
    match = re.search(r"(?m)^id ([0-9]+),", output or "")
    return int(match.group(1)) if match else None


def parse_sink_mute(output):
    if output is None or not output.startswith("Volume:"):
        return "unknown"
    return "yes" if "[MUTED]" in output else "no"


def is_bluetooth(props):
    return bool(props.get("api.bluez5.address")
                or props.get("api.bluez5.profile")
                or props.get("device.api") == "bluez5")


def graph_snapshot(objects, sink_id, source_id, sink_muted, call_present):
    """Return only anonymous counts, states, and booleans."""
    nodes = {}
    links = []
    for obj in objects:
        info = obj.get("info") or {}
        if obj.get("type") == "PipeWire:Interface:Node":
            nodes[obj.get("id")] = info
        elif obj.get("type") == "PipeWire:Interface:Link":
            links.append(info)

    def props(nid):
        return (nodes.get(nid) or {}).get("props") or {}

    outputs = {nid: info for nid, info in nodes.items()
               if str((info.get("props") or {}).get("media.class") or "")
               == "Stream/Output/Audio"}
    connected_outputs = {link.get("output-node-id") for link in links
                         if link.get("input-node-id") == sink_id
                         and link.get("output-node-id") in outputs
                         and link.get("state") in ("active", "paused", "init")}
    bt_nodes = [info for info in nodes.values()
                if is_bluetooth(info.get("props") or {})]
    hfp_nodes = [info for info in bt_nodes
                 if (info.get("props") or {}).get("api.bluez5.profile")
                 == "headset-head-unit"]
    sink_state = (nodes.get(sink_id) or {}).get("state")
    if sink_state not in ("running", "idle", "suspended", "error"):
        sink_state = "unknown"
    return {
        "call_present": call_present,
        "default_sink_present": "yes" if sink_id is not None else "no",
        "default_sink_is_bluetooth": "yes" if is_bluetooth(props(sink_id)) else "no",
        "default_sink_state": sink_state,
        "default_sink_muted": sink_muted,
        "default_source_present": "yes" if source_id is not None else "no",
        "default_source_is_bluetooth": "yes" if is_bluetooth(props(source_id)) else "no",
        "output_streams": len(outputs),
        "output_streams_running": sum(i.get("state") == "running"
                                      for i in outputs.values()),
        "output_streams_suspended": sum(i.get("state") == "suspended"
                                        for i in outputs.values()),
        "direct_output_stream_links_to_sink": len(connected_outputs),
        "bluetooth_nodes": len(bt_nodes),
        "hfp_nodes": len(hfp_nodes),
    }


def find_gateway():
    output = command(["busctl", "--user", "call", TELEPHONY,
                      "/org/pipewire/Telephony", "org.ofono.Manager", "GetModems"])
    gateways = sorted(set(AG_PATH.findall(output or "")))
    return gateways[0] if len(gateways) == 1 else None


def call_present(gateway):
    if gateway is None:
        return "unknown"
    output = command(["busctl", "--user", "call", TELEPHONY, gateway,
                      "org.ofono.VoiceCallManager", "GetCalls"])
    if output is None:
        return "unknown"
    return "yes" if CALL_PATH.search(output) else "no"


def sample(gateway):
    raw = command(["pw-dump"])
    if raw is None:
        return None
    try:
        objects = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(objects, list):
        return None
    sink = parse_wpctl_id(command(["wpctl", "inspect", "@DEFAULT_AUDIO_SINK@"]))
    source = parse_wpctl_id(command(["wpctl", "inspect", "@DEFAULT_AUDIO_SOURCE@"]))
    muted = parse_sink_mute(command(["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"]))
    return graph_snapshot(objects, sink, source, muted, call_present(gateway)), sink, source


def emit(index, elapsed, state, first_sink, sink, first_source, source):
    print("sample=" + str(index), flush=True)
    print("elapsed_seconds=" + str(int(elapsed)), flush=True)
    print("default_sink_changed=" + ("yes" if sink != first_sink else "no"), flush=True)
    print("default_source_changed=" + ("yes" if source != first_source else "no"), flush=True)
    for name, value in state.items():
        print(f"{name}={value}", flush=True)
    print("sample_end=yes", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seconds", type=int, default=35)
    parser.add_argument("--interval-ms", type=int, default=500)
    args = parser.parse_args()
    if not (5 <= args.seconds <= 90) or not (250 <= args.interval_ms <= 2000):
        parser.error("--seconds 5..90; --interval-ms 250..2000")
    if not all(shutil.which(cmd) for cmd in ("pw-dump", "wpctl", "busctl")):
        print("probe_complete=no")
        print("probe_error=read_only_tool_missing")
        return 1

    print("nativepair_call_audio_watch_schema=1")
    print("personal_payload_printed=no")
    print("audio_configuration_changed=no")
    print("call_performed=no")
    gateway = find_gateway()
    print("telephony_gateway_resolved=" + ("yes" if gateway else "no"))
    start = time.monotonic()
    first_sink = first_source = None
    previous = None
    count = failures = transitions = 0
    call_seen = mute_seen = sink_changed = hfp_seen = stream_disruption = False
    try:
        while time.monotonic() - start < args.seconds:
            result = sample(gateway)
            if result is None:
                failures += 1
            else:
                state, sink, source = result
                if count == 0:
                    first_sink, first_source = sink, source
                count += 1
                call_seen |= state["call_present"] == "yes"
                mute_seen |= state["default_sink_muted"] == "yes"
                sink_changed |= sink != first_sink
                hfp_seen |= state["hfp_nodes"] > 0
                stream_disruption |= (state["output_streams_suspended"] > 0
                                      or (state["output_streams"] > 0
                                          and state["output_streams_running"] == 0))
                comparison = (state, sink, source)
                if comparison != previous:
                    emit(count, time.monotonic() - start, state,
                         first_sink, sink, first_source, source)
                    transitions += 1
                previous = comparison
            time.sleep(args.interval_ms / 1000)
    except KeyboardInterrupt:
        print("probe_complete=interrupted")
        return 130
    print(f"snapshots_succeeded={count}")
    print(f"snapshots_failed={failures}")
    print(f"observed_state_versions={transitions}")
    print("call_observed=" + ("yes" if call_seen else "no"))
    print("sink_muted_at_any_time=" + ("yes" if mute_seen else "no"))
    print("default_sink_changed_at_any_time=" + ("yes" if sink_changed else "no"))
    print("hfp_nodes_observed=" + ("yes" if hfp_seen else "no"))
    print("output_stream_disruption_observed=" +
          ("yes" if stream_disruption else "no"))
    print("probe_complete=" + ("yes" if count else "no"))
    print("note=read_only_no_audio_names_addresses_or_call_data")
    return 0 if count else 1


if __name__ == "__main__":
    raise SystemExit(main())
