import logging
from typing import Any
from .base import BaseConsumerQueued
from periphery import GPIO

LOGGER = logging.getLogger(__name__)


def _cfg_to_bool(value):
    # False:
    #  - value == 0, "0", "False", False
    # All other => True
    if isinstance(value, bool):
        return value

    # check for 0 or "0"
    try:
        return bool(int(value))
    except ValueError:
        # value is not integer
        pass

    if isinstance(value, str):
        if value == "False":
            return False

    return True


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
        LOGGER.info("%s: activated", name)
        LOGGER.debug(self.events_config)

    def handle_event(self, event_name: str, data: Any):
        message = f"Event='{event_name}', data='{data}'"
        LOGGER.debug(message)

        evt_cfg = self.events_config.get(event_name, -1)
        if evt_cfg is not -1:
            if isinstance(evt_cfg, dict):
                if evt_cfg.get("enabled", True) is False:
                    LOGGER.info("Event '%s' disabled", event_name)
                    return
            LOGGER.info(message)


class GenericOutput(BaseConsumerQueued):
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
        try:
            line = int(config["line"])
        except KeyError as e:
            raise ValueError("line: No 'line' parameter set!") from e
        except ValueError as e:
            raise ValueError(
                f"line: Invalid value ('{config['line']}')."
            ) from e

        chip_path = config.get("path", "/dev/gpiochip0")
        self.pin_out = GPIO(chip_path, line, "out")

        out_value = bool(config.get("default_value", False))
        self.pin_out.write(out_value)
        LOGGER.info(
            "%s: Output %s line %s (default value %s)",
            name,
            chip_path,
            line,
            out_value,
        )

    def handle_event(self, event_name: str, data: Any):
        message = f"Event='{event_name}', data='{data}'"
        LOGGER.debug(message)

        evt_cfg = self.events_config.get(event_name, -1)
        if evt_cfg is not -1:
            if isinstance(evt_cfg, dict):
                if evt_cfg.get("enabled", True) is False:
                    LOGGER.info("Event '%s' disabled", event_name)
                    return
                LOGGER.info(message)
                val = bool(evt_cfg.get("value", False))
                self.pin_out.write(val)
