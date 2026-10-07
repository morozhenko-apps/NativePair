"""Synthetic graph and output sanitization tests for passive audio watcher."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import probe_call_audio_watch as watcher


def node(identifier, role, state="running", **props):
    return {"id": identifier, "type": "PipeWire:Interface:Node",
            "info": {"state": state, "props": {"media.class": role, **props}}}


def link(output_id, sink_id, state="active"):
    return {"type": "PipeWire:Interface:Link",
            "info": {"output-node-id": output_id, "input-node-id": sink_id,
                     "state": state}}


class WatcherTests(unittest.TestCase):
    def test_id_and_mute_parsers(self):
        self.assertEqual(watcher.parse_wpctl_id("id 41, type PipeWire:Interface:Node"), 41)
        self.assertIsNone(watcher.parse_wpctl_id(""))
        self.assertEqual(watcher.parse_sink_mute("Volume: 0.50"), "no")
        self.assertEqual(watcher.parse_sink_mute("Volume: 0.50 [MUTED]"), "yes")
        self.assertEqual(watcher.parse_sink_mute(None), "unknown")

    def test_healthy_playback(self):
        graph = [node(41, "Audio/Sink"), node(42, "Audio/Source"),
                 node(50, "Stream/Output/Audio"), link(50, 41)]
        result = watcher.graph_snapshot(graph, 41, 42, "no", "no")
        self.assertEqual(result["output_streams_running"], 1)
        self.assertEqual(result["direct_output_stream_links_to_sink"], 1)
        self.assertEqual(result["default_sink_is_bluetooth"], "no")
        self.assertEqual(result["default_sink_state"], "running")

    def test_call_interruption(self):
        graph = [node(41, "Audio/Sink", state="suspended"),
                 node(50, "Stream/Output/Audio", state="suspended"),
                 node(60, "Audio/Source", **{
                     "api.bluez5.address": "00:11:22:33:44:55",
                     "api.bluez5.profile": "headset-head-unit",
                 })]
        result = watcher.graph_snapshot(graph, 41, None, "yes", "yes")
        self.assertEqual(result["default_sink_muted"], "yes")
        self.assertEqual(result["output_streams_suspended"], 1)
        self.assertEqual(result["direct_output_stream_links_to_sink"], 0)
        self.assertEqual(result["hfp_nodes"], 1)
        self.assertNotIn("00:11:22:33:44:55", str(result))

    def test_call_preserves_local_route(self):
        graph = [node(41, "Audio/Sink"), node(50, "Stream/Output/Audio"),
                 node(60, "Audio/Source", **{
                     "api.bluez5.profile": "headset-head-unit",
                 }), link(50, 41)]
        result = watcher.graph_snapshot(graph, 41, None, "no", "yes")
        self.assertEqual(result["default_sink_is_bluetooth"], "no")
        self.assertEqual(result["output_streams_running"], 1)
        self.assertEqual(result["hfp_nodes"], 1)

    def test_missing_graph(self):
        result = watcher.graph_snapshot([], None, None, "unknown", "unknown")
        self.assertEqual(result["default_sink_state"], "unknown")
        self.assertEqual(result["output_streams"], 0)
        self.assertEqual(result["default_sink_present"], "no")


if __name__ == "__main__":
    unittest.main()
