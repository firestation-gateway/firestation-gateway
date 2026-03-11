from typing import Any, Optional
from .genius import Genius
from .generic_input import GenericInput


def get_producer(ptype: str) -> Optional[Any]:
    return {"genius": Genius, "generic-input": GenericInput}.get(ptype)
