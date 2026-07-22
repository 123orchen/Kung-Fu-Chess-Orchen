"""A minimal, synchronous publish/subscribe bus.

Different parts of the server (score updates, move-log updates, sound
triggers, game start/end animations, ...) can subscribe to named events
without knowing about each other. Whoever causes the event just calls
`publish`; every subscriber registered for that event name gets called.

This is intentionally small - no async, no priorities, no once-only
subscriptions - because right now it only needs to support a basic
"move happened" event. More event types can subscribe/publish the same
way as later stages (score, sound, animations) are added.
"""
import threading
from collections import defaultdict


class Bus:
    def __init__(self):
        self._subscribers = defaultdict(list)
        self._lock = threading.Lock()

    def subscribe(self, event_type: str, callback):
        """Register `callback(data)` to be called whenever `event_type` is published."""
        with self._lock:
            self._subscribers[event_type].append(callback)

    def publish(self, event_type: str, data=None):
        """Call every subscriber registered for `event_type` with `data`."""
        with self._lock:
            callbacks = list(self._subscribers.get(event_type, ()))
        for callback in callbacks:
            callback(data)
