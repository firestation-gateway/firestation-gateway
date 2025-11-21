import json
import logging
import requests
# from .model import OperationModel

URL = "https://connectapi.feuersoftware.com/interfaces/public"

LOG = logging.getLogger(__name__)


class ConnectApiClient:
    def __init__(self, token: str):
        self.header = {
            "Authorization": f"bearer {token}",
            "Accept": "application/json",
            "Content-type": "application/json",
        }

    def _request(self, url: str, data: str):
        r = requests.post(url, data=data, headers=self.header, timeout=10.0)
        if r.status_code != 204:
            LOG.error("'%s' [%s] - %s", url, r.status_code, r.text)
        r.raise_for_status()
        return r

    def send_operation(self, data: dict):
        # TODO: check data with model.py
        return self._request(URL + "/operation", json.dumps(data))
