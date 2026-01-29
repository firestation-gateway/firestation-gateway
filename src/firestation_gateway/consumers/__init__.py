from typing import Any
from .tetracontrol import Tetracontrol
from .connect import Connect
from .generic_output import GenericPrintout, GenericOutput


def get_consumer(ctype: str) -> Any:
    return {
        "tetracontrol": Tetracontrol,
        "connect": Connect,
        "generic-printout": GenericPrintout,
        "generic-output": GenericOutput,
    }.get(ctype, None)
