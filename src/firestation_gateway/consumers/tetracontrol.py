import logging
from typing import Any
import requests
from firestation_gateway import tetracontrol

from .base import BaseConsumerQueued


LOGGER = logging.getLogger(__name__)

sds_callout_prototype = {
    "Ziel": "",
    "Text": "",
    "Typ": tetracontrol.TETRAcontrolSDSTyp.CALLOUT,
    "Prio": 1,
    "Flash": 1,
    "COPrio": 1,
    "CONum": 123,
}
sds_prototype = {
    "Ziel": "",
    "Text": "",
    "Typ": tetracontrol.TETRAcontrolSDSTyp.NORMAL,
    "Prio": 1,
    "Flash": 1,
}


class Tetracontrol(BaseConsumerQueued):
    def __init__(
        self,
        name: str,
        emitter,
        events_config,
        config,
    ):
        super().__init__(name, emitter, events_config)
        self.events_config = events_config
        self.token = config.get("token")
        self.url = config.get("url")
        self.testmode = config.get("testmode", False)
        if self.testmode:
            LOGGER.warning(
                "Tetracontrol: Testmode enabled! No real alarm is sent."
            )
        self.tetracontrol = tetracontrol.TETRAcontrolClient(
            self.url, self.token
        )
        # counter for all alarm events
        self.alarm_number = 1

        # test connection to tetracontrol. TODO: remove later
        try:
            r = self.tetracontrol.device_status()
            print(r.text)
        except requests.exceptions.ConnectionError as e:
            LOGGER.error(e)
            # LOG.exception(e)
        except requests.exceptions.HTTPError as e:
            LOGGER.error(e)
        except requests.exceptions.InvalidURL as e:
            LOGGER.error(e)

    def handle_event(self, event_name: str, data: Any):
        message = f"Event='{event_name}', data='{data}'"
        LOGGER.debug(message)

        evt_cfg = self.events_config.get(event_name)
        if evt_cfg is not None:
            if evt_cfg.get("enabled", True) is False:
                return
            # event is set within config
            if evt_cfg.get("type") == "callout":
                sds = sds_callout_prototype.copy()
                # only callout support CONum and sub
                sds["CONum"] = self.alarm_number
                text = "".join(evt_cfg.get("sub", ""))
                self.alarm_number += 1
            else:
                # default if not set
                sds = sds_prototype.copy()
                text = ""

            sds["Text"] = text + evt_cfg.get("text")
            sds["Ziel"] = evt_cfg.get("dest")

            LOGGER.info(sds)
            if not self.testmode:
                try:
                    r = self.tetracontrol.sds(sds)
                    LOGGER.info(r.text)
                except requests.exceptions.ConnectionError as e:
                    LOGGER.error(e)
                except requests.exceptions.HTTPError as e:
                    LOGGER.error(e)
