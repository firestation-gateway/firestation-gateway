import logging
from typing import Any
from .base import BaseConsumerQueued

LOGGER = logging.getLogger(__name__)


class GenericPrintout(BaseConsumerQueued):
    def __init__(
        self,
        name: str,
        emitter,
        events_config,
        config,
    ):
        super().__init__(name, emitter, events_config)
        self.events_config = events_config
        _ = config

    def handle_event(self, event_name: str, data: Any):
        message = f"Event='{event_name}', data='{data}'"
        LOGGER.debug(message)

        evt_cfg = self.events_config.get(event_name)
        if evt_cfg is not None:
            if evt_cfg.get("enabled", True) is False:
                return
            LOGGER.info(message)
