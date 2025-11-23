import threading
import time
import logging
from pathlib import Path
from typing import Any, Dict
from periphery import GPIO

LOGGER = logging.getLogger(__name__)

TIMER_PERIOD = 0.1
COUNTER_VALUE_ACTIVE = 1.0 / TIMER_PERIOD
COUNTER_VALUE_ALARM = 8.0 / TIMER_PERIOD + COUNTER_VALUE_ACTIVE


class GeniusState:
    IDLE, ACTIVE, ALARM = range(3)


class Genius(threading.Thread):
    STATE_IDLE, STATE_ACTIVE, STATE_ALARM = range(3)

    def __init__(
        self,
        name: str,
        emitter: Any,
        events_config: Dict[str, Dict[str, Any]],
        config: Dict[str, Any],
    ) -> None:
        super().__init__(name=name)
        self.emitter = emitter
        self.config = config
        self.events_config = events_config
        self.running = True

        self.events: Dict[str, Any] = config.get("events", {})
        try:
            line = int(config.get("line", -1))
        except ValueError:
            line = -1

        if line >= 0:
            self.pin_in = GPIO("/dev/gpiochip0", line, "in", inverted=True)
        else:
            self.pin_in = None
        self._state = GeniusState.IDLE
        self._btn_counter = 0
        self._sampling_interval = TIMER_PERIOD
        logging.info("Genius: line=%s", line)

    def _read_input(self):
        if self.pin_in is not None:
            return self.pin_in.read()
        # simulate pin state
        my_file = Path("/tmp/genius_active.tmp")
        if my_file.is_file():
            return True
        return False

    def _state_machine(self):
        pending = GeniusState.IDLE
        if self._btn_counter > COUNTER_VALUE_ACTIVE:
            pending = GeniusState.ACTIVE
        if self._btn_counter > COUNTER_VALUE_ALARM:
            pending = GeniusState.ALARM

        # state machine

        if pending == GeniusState.IDLE and self._state == GeniusState.ACTIVE:
            # transion from ACTIV -> IDLE
            # this is a selftest
            LOGGER.debug("EVT: Selftest")

            self.emitter.emit(
                self.name.lower() + "_selftest",
                {"time": time.asctime(), "source": self.name},
            )

        if pending == GeniusState.IDLE and self._state != GeniusState.IDLE:
            # transion from Any-State -> IDLE
            LOGGER.info("STATE: Idle")
            LOGGER.debug("EVT: Idle")
            self.emitter.emit(
                self.name.lower() + "_idle", {"time": time.asctime(), "source": self.name}
            )
        elif (
            pending == GeniusState.ACTIVE and self._state != GeniusState.ACTIVE
        ):
            # transion from Any-State -> ACTIVE
            LOGGER.info("STATE: Active")
        elif pending == GeniusState.ALARM and self._state != GeniusState.ALARM:
            # transion from Any-State -> ALARM
            LOGGER.info("STATE: Alarm")
            # sending event on state alarm
            self.emitter.emit(
                self.name.lower() + "_alarm", {"time": time.asctime(), "source": self.name}
            )

        if self._state != pending:
            LOGGER.debug("New state: %d -> %d", self._state, pending)

        self._state = pending

    def run(self) -> None:
        while self.running:
            t_start = time.time()

            if self._read_input():
                self._btn_counter += 1
            else:
                self._btn_counter = 0
            self._state_machine()

            # wait until next sampling point
            elapsed = time.time() - t_start
            sleep_time = self._sampling_interval - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

    def stop(self) -> None:
        self.running = False
