"""Address schemas module."""

from .get import AddressGet
from .patch import AddressPatch
from .post import AddressPost
from .put import AddressPut

__all__ = ("AddressGet", "AddressPatch", "AddressPost", "AddressPut")
