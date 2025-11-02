"""System responses schemas module."""

from .health import HealthResponse
from .unhealth import UnhealthResponse
from .version import VersionResponse

__all__ = ("HealthResponse", "UnhealthResponse", "VersionResponse")
