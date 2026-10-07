# Passive HFP call-audio observation

A read-only, **optional** watcher for before/during/after HFP call-audio diagnosis. It never
dials, activates SCO, changes routing or volumes, or records voice payloads.
Raw PipeWire and D-Bus data are processed in memory and never printed or stored.

Run the watcher in one terminal:

    ./scripts/probe-call-audio-watch.sh --seconds 35

An independently approved real-call test can run in a second terminal while
the watcher is sampling. No dial operation may be performed without fresh
explicit approval. Never treat running the watcher as permission to dial.

The watcher prints only anonymous counts and state enums on changes, plus a
bounded summary. Compare call_present before, during and after the call, along
with sink mute, sink/source target changes, stream running/suspended states,
direct output stream links to the default sink, and HFP nodes.

Direct link counts are not a full patchbay graph: filters or virtual nodes
can create indirect playback routes. Zero direct links is not necessarily
proof of silence. The watcher cannot infer audibility from stream state alone.

If Telephony exposes no uniquely identifiable AudioGateway object, call
presence is unknown rather than no. The script does not print any gateway
identity, device address, application name or call metadata.

Defaults: 35 seconds, 500 ms sample spacing. Accepted options are seconds
5..90 and interval-ms 250..2000. Ctrl+C safely stops observation.

Important observation: the initial Dial/Hangup-only test took focus from a game
that normally stops playback when minimized/out of focus. The temporary game
silence during the call is consistent with normal game focus behavior. Do not
repeat a real call solely to diagnose that expected behavior or treat it as a
PipeWire/SCO regression. Use this watcher only for independently unexplained
audio behavior, with fresh explicit approval for any actual call.
