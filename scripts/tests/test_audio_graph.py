"""Shared node decoder contracts, independent of PipeWire and the filesystem."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from scenarios import add_cases, category

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import probe_audio_graph as graph


def node(identifier=41, info=None):
    return {"id": identifier, "type": "PipeWire:Interface:Node", "info": info}


class GraphContracts(unittest.TestCase):
    @category("N12")
    def test_given_missing_file_when_nodes_loaded_then_io_failure_is_explicit(self):
        with self.assertRaises(FileNotFoundError):
            graph.load_nodes("/missing/PRIVATE_CONTACT")

    @category("N12")
    def test_given_permission_failure_when_nodes_loaded_then_error_is_not_hidden(self):
        with patch("builtins.open", side_effect=PermissionError("PRIVATE_CONTACT")):
            with self.assertRaises(PermissionError):
                graph.load_nodes("fake")

    @category("N6")
    def test_given_bad_json_when_nodes_loaded_then_decode_failure_is_explicit(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "snapshot.json"
            path.write_text("PRIVATE_CONTACT")
            with self.assertRaises(json.JSONDecodeError):
                graph.load_nodes(path)

    @category("N10")
    def test_given_private_properties_when_nodes_loaded_then_no_payload_is_printed(self):
        expected = [node(info={"props": {"node.name": "PRIVATE_CONTACT"}})]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "snapshot.json"
            path.write_text(json.dumps(expected))
            output = io.StringIO()
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                self.assertEqual(graph.load_nodes(path), expected)
        self.assertEqual(output.getvalue(), "")


def valid(self, value):
    data, expected = value
    self.assertEqual(graph.valid_nodes(data), expected)


add_cases(GraphContracts, "Positive", "nodes_normalized", [
    ("empty_list", ([], [])),
    ("missing_info", ([node()], [node(info={"props": {}})])),
    ("missing_properties", ([node(info={"state": "idle"})], [node(info={"state": "idle", "props": {}})])),
    ("null_properties", ([node(info={"props": None})], [node(info={"props": {}})])),
    ("full_properties", ([node(info={"props": {"media.class": "Audio/Sink"}, "state": "running"})],
                          [node(info={"props": {"media.class": "Audio/Sink"}, "state": "running"})])),
    ("duplicate_ids", ([node(41, {"state": "idle"}), node(41, {"state": "running"})],
                        [node(41, {"state": "running", "props": {}})])),
    ("minimum_id", ([node(0)], [node(0, {"props": {}})])),
    ("maximum_id", ([node(4294967295)], [node(4294967295, {"props": {}})])),
    ("large_graph", ([node(i) for i in range(1000)], [node(i, {"props": {}}) for i in range(1000)])),
], valid)
add_cases(GraphContracts, "N6", "bad_entries_filtered", [
    ("invalid_entry_" + str(index), ([entry], []))
    for index, entry in enumerate((None, 1, [], "PRIVATE_CONTACT", {},
        {"type": "PipeWire:Interface:Link", "id": 1},
        {"type": "Other", "id": 1},
        node(None), node(True), node(False), node(-1), node(4294967296), node("41"), node([]), node({}), node(1.5),
        node(41, "PRIVATE_CONTACT"), node(41, []), node(41, 0),
        node(41, {"props": "PRIVATE_CONTACT"}), node(41, {"props": []}), node(41, {"props": 0}),
    ))], valid)


def invalid_root(self, data):
    with self.assertRaisesRegex(ValueError, "^invalid_graph$"):
        graph.valid_nodes(data)


add_cases(GraphContracts, "N6", "invalid_root_rejected", [
    ("invalid_root_" + str(index), data)
    for index, data in enumerate((None, 1, {}, "PRIVATE_CONTACT", True, 1.5))], invalid_root)
