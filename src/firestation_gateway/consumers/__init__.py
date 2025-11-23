from typing import Any
from .tetracontrol import Tetracontrol
from .connect import Connect
from .generic_output import GenericPrintout


def get_consumer(ctype: str) -> Any:
    return {
        "tetracontrol": Tetracontrol,
        "connect": Connect,
        "generic-output": GenericPrintout,
    }.get(ctype, None)
