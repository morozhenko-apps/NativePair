"""Shared strict node decoding for read-only feasibility audio classifiers."""
import json


def valid_nodes(data):
    """Return distinct valid nodes; malformed entries never prove endpoints."""
    if not isinstance(data, list):
        raise ValueError("invalid_graph")
    nodes = {}
    for obj in data:
        if not isinstance(obj, dict) or obj.get("type") != "PipeWire:Interface:Node":
            continue
        identifier = obj.get("id")
        if type(identifier) is not int or not 0 <= identifier <= 4294967295:
            continue
        info = obj.get("info")
        if info is None:
            info = {}
        if not isinstance(info, dict):
            continue
        props = info.get("props")
        if props is None:
            props = {}
        if not isinstance(props, dict):
            continue
        nodes[identifier] = {"id": identifier, "type": "PipeWire:Interface:Node",
                             "info": {**info, "props": props}}
    return list(nodes.values())


def load_nodes(path):
    """Read locally; callers translate I/O/JSON errors into anonymous enums."""
    with open(path, encoding="utf-8") as handle:
        return valid_nodes(json.load(handle))
