from .core import main

__version__ = "1.0.0"
__version_info__ = tuple(int(i) for i in __version__.split(".") if i.isdigit())

__all__ = ["main"]
