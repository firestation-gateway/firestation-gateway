import logging
import dataclasses
import requests
from .model import SDSCalloutModel, SDSModel, RadioModel

LOG = logging.getLogger(__name__)


class TETRAcontrolSDSTyp:
    SIMPLE = 0
    NORMAL = 1
    CONCAT = 138
    CALLOUT = 195


class TETRAcontrolClient:
    def __init__(self, url: str, token: str):
        self.cookies = {"userkey": token}
        self.server = url
        # send SDS encrypted
        self.sds_enc = True
        # default device id (1-6)
        # TODO: make configurable
        self.device_id = 1

    def _request(self, url, data, timeout):
        r = requests.post(
            url,
            data=data,
            cookies=self.cookies,
            timeout=timeout,
        )
        if r.status_code != 200:
            LOG.error("'%s' [%s] - %s", url, r.status_code, r.text)
        else:
            LOG.debug("'%s' [%s] - %s", url, r.status_code, r.text)
        r.raise_for_status()
        return r

    def sds(self, data: dict, timeout: float = 10.0):
        url = f"{self.server}/API/SDS"
        if "Typ" in data and data["Typ"] == 195:
            _dat = SDSCalloutModel(**data)
        else:
            _dat = SDSModel(**data)
        return self._request(url, dataclasses.asdict(_dat), timeout)

    def device_status(self, device_id=1, timeout: float = 10.0):
        url = f"{self.server}/API/RADIO.json"
        _dat = RadioModel(GerID=device_id)
        return self._request(url, dataclasses.asdict(_dat), timeout)

    def issi_status(self, used_filter: str, timeout: float = 10.0):
        url = f"{self.server}/API/issi.json"
        _dat = {"filter": used_filter}
        return self._request(url, _dat, timeout)
