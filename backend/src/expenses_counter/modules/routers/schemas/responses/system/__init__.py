"""System responses schemas module."""

__all__ = ("HealthResponse", "LoginResponse", "UnhealthResponse", "VersionResponse")

from .health import HealthResponse
from .login_response import LoginResponse
from .unhealth import UnhealthResponse
from .version import VersionResponse
