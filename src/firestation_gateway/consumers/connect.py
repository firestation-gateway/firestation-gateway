import logging
import datetime
from typing import Any
import requests
from firestation_gateway import connectapi

from .base import BaseConsumerQueued


LOGGER = logging.getLogger(__name__)


operation = {
    "Start": "",
    "Status": "new",
    "AlarmEnabled": True,
    "Keyword": "F-RWM",
    "Address": {
        "Street": "Hauptstr.",
        "HouseNumber": "112",
        "ZipCode": "112112",
        "City": "Musterstadt",
    },
    "Source": "Pi Fwh Musterstadt",
    "Facts": "Meldereingang",
    "Ric": "0000000",
    "Properties": [{"Key": "Quelle-intern", "Value": "Rasp Pi Fwh"}],
}


class Connect(BaseConsumerQueued):
    def __init__(
        self,
        name: str,
        emitter,
        events_config,
        config,
    ):
        super().__init__(name, emitter, events_config)
        self.events_config = events_config
        self.testmode = config.get("testmode", False)
        if self.testmode:
            LOGGER.warning(
                "ConnectApi: Testmode enabled! No real alarm is sent."
            )
        self.connectapi = connectapi.ConnectApiClient(config.get("token"))

    def handle_event(self, event_name: str, data: Any):
        message = f"Event='{event_name}', data='{data}'"
        LOGGER.debug(message)

        evt_cfg = self.events_config.get(event_name)
        if evt_cfg is not None:
            if evt_cfg.get("enabled", True) is False:
                return
            # event is set within config

            op = operation.copy()
            op["Start"] = datetime.datetime.now().isoformat()
            op["Ric"] = evt_cfg.get("ric")
            op["Keyword"] = evt_cfg.get("keyword")
            op["Facts"] = evt_cfg.get("facts")
            op["Source"] = evt_cfg.get("source")
            if evt_cfg.get("address", False):
                op["Address"]["Street"] = evt_cfg["address"].get("street", "")
                op["Address"]["HouseNumber"] = evt_cfg["address"].get(
                    "housenumber", ""
                )
                op["Address"]["ZipCode"] = evt_cfg["address"].get(
                    "zipcode", ""
                )
                op["Address"]["City"] = evt_cfg["address"].get("city", "")

            LOGGER.info(op)
            if not self.testmode:
                try:
                    self.connectapi.send_operation(op)
                except requests.exceptions.ConnectionError as e:
                    LOGGER.error(e)
                except requests.exceptions.HTTPError as e:
                    LOGGER.error(e)
