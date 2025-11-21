from typing import Any
from .tetracontrol import Tetracontrol
from .connect import Connect


def get_consumer(ctype: str) -> Any:
    return {
        "tetracontrol": Tetracontrol,
        "connect": Connect,
    }.get(ctype, None)
