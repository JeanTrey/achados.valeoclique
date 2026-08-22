"""Vale o Clique Video Engine core package."""

from .loader import load_project
from .validators import ValidationError

__all__ = ["ValidationError", "load_project"]
