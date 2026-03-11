import threading
import queue
from typing import Any


class BaseConsumerQueued(threading.Thread):
    def __init__(self, name: str, emitter, events_config):
        super().__init__(name=name)
        self.emitter = emitter
        self.running = True
        self.event_queue = queue.Queue()
        for event_name in events_config:
            # Add all configured events
            # Note: each handler runs in the context of the emitter.
            emitter.on(event_name, self._create_handler(event_name))

    # this function runs in the context of the emitter
    def _create_handler(self, event_name):
        def handler(data):
            self.event_queue.put((event_name, data))

        return handler

    def run(self):
        """Main loop handling all events from queue."""
        while self.running:
            event_name, data = self.event_queue.get()
            self.handle_event(event_name, data)

    def stop(self):
        """Stop running thread."""
        self.running = False
        # send fake event to queue for release q.get()
        self.event_queue.put(("system_stop", None))

    def handle_event(self, event_name: str, data: Any):
        pass
