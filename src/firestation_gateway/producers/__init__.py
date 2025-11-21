from typing import Any, Optional
from .genius import Genius


def get_producer(ptype: str) -> Optional[Any]:
    return {"genius": Genius}.get(ptype)
