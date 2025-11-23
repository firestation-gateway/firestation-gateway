import threading
import time
import logging
from pathlib import Path
from typing import Any, Dict
from periphery import GPIO

LOGGER = logging.getLogger(__name__)

TIMER_PERIOD = 0.1


class GenericInputState:
    IDLE, ACTIVE, ALARM = range(3)


class GenericInput(threading.Thread):
    STATE_IDLE, STATE_ACTIVE, STATE_ALARM = range(3)

    def __init__(
        self,
        name: str,
        emitter: Any,
        events_config: list,
        config: Dict[str, Any],
    ) -> None:
        super().__init__(name=name)
        self.emitter = emitter
        self.config = config
        self.events = events_config
        self.running = True

        bias = config.get("bias", "default")
        if bias not in ["pull_up", "pull_down", "default"]:
            raise ValueError(
                "bias: Invalid value. Use 'pull_up', 'pull_down' or 'default'"
            )

        active_low = config.get("active_low", True)
        if active_low:
            active_low = True
        else:
            active_low = False

        try:
            self.time_debounce = int(config.get("time_debounce", 500))
        except ValueError:
            LOGGER.warning("time_debounce: Invalid set to 500ms.")
            self.time_debounce = 500

        try:
            self.time_alarm = int(config.get("time_alarm", "NICH VORHANDEN"))
        except ValueError as e:
            raise ValueError("alarm_time: Invalid value.") from e

        try:
            line = int(config.get("line", -1))
        except ValueError as e:
            raise ValueError("line: Invalid value.") from e

        if line >= 0:
            self.pin_in = GPIO(
                "/dev/gpiochip0", line, "in", inverted=active_low, bias=bias
            )
        else:
            self.pin_in = None

        self.cnt_active = (self.time_debounce / 1000.0) / TIMER_PERIOD
        self.cnt_alarm = (
            self.time_alarm / 1000.0
        ) / TIMER_PERIOD + self.cnt_active

        self._state = GenericInputState.IDLE
        self._btn_counter = 0
        self._sampling_interval = TIMER_PERIOD
        logging.info("%s: line=%s", name, line)
        logging.debug(self.pin_in)

    def _read_input(self):
        if self.pin_in is not None:
            return self.pin_in.read()
        # simulate pin state
        my_file = Path("/tmp/firestation_gw_" + self.name.lower() + "_active")
        if my_file.is_file():
            return True
        return False

    def _state_machine(self):
        pending = GenericInputState.IDLE
        if self._btn_counter > self.cnt_active:
            pending = GenericInputState.ACTIVE
        if self._btn_counter > self.cnt_alarm:
            pending = GenericInputState.ALARM

        # state machine
        if (
            self._state == GenericInputState.IDLE
            and pending == GenericInputState.ACTIVE
        ):
            LOGGER.info("STATE: Idle -> Active")
        elif (
            self._state == GenericInputState.ACTIVE
            and pending == GenericInputState.ALARM
        ):
            LOGGER.info("STATE: Active -> Alarm")
            self.emitter.emit(
                self.name.lower() + "_alarm",
                {"time": time.asctime(), "source": self.name},
            )
        if (
            pending == GenericInputState.IDLE
            and self._state != GenericInputState.IDLE
        ):
            LOGGER.info("STATE: -> Idle")
            self.emitter.emit(
                self.name.lower() + "_idle",
                {"time": time.asctime(), "source": self.name},
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
