"""Unit tests for ``PasswordService``."""

import hashlib
import hmac

import pytest

from expenses_counter.services.auth import PasswordService


@pytest.fixture
def secret_key() -> str:
    """Return a stable secret key for password tests.

    Returns:
        str: Secret key used to seed HMAC hashing.

    """
    return "super-secret-test-key"


@pytest.fixture
def password_service(secret_key: str) -> PasswordService:
    """Return a ``PasswordService`` built from the test secret key.

    Args:
        secret_key: HMAC secret used by the service.

    Returns:
        PasswordService: Configured service ready for hashing.

    """
    return PasswordService(secret_key)


class TestPasswordServiceInit:
    """Test ``PasswordService.__init__``."""

    def test_accepts_str_secret(self, secret_key: str) -> None:
        """A string secret should be stored as UTF-8 encoded bytes."""
        service = PasswordService(secret_key)
        assert service.secret_key == secret_key.encode("utf-8")

    def test_accepts_bytes_secret(self) -> None:
        """A bytes secret should be stored verbatim."""
        secret_bytes = b"already-bytes"
        service = PasswordService(secret_bytes)
        assert service.secret_key == secret_bytes


class TestHashPassword:
    """Test ``PasswordService.hash_password``."""

    def test_hash_is_deterministic(self, password_service: PasswordService) -> None:
        """Hashing the same password twice yields the same digest."""
        assert password_service.hash_password("password") == password_service.hash_password("password")

    def test_hash_returns_hex_string(self, password_service: PasswordService) -> None:
        """The digest must be a lowercase hex string of SHA-256 length."""
        hashed = password_service.hash_password("password")
        assert isinstance(hashed, str)
        assert len(hashed) == 64
        int(hashed, 16)  # raises ValueError if not hex

    def test_hash_differs_for_different_passwords(self, password_service: PasswordService) -> None:
        """Different inputs must produce different digests."""
        assert password_service.hash_password("a") != password_service.hash_password("b")

    def test_hash_differs_for_different_keys(self) -> None:
        """The same password under different keys yields different digests."""
        a = PasswordService("key-a").hash_password("same-password")
        b = PasswordService("key-b").hash_password("same-password")
        assert a != b

    def test_hash_matches_reference_hmac(self, password_service: PasswordService, secret_key: str) -> None:
        """The digest must match a direct ``hmac.new(...).hexdigest()`` calculation."""
        password = "password"
        expected = hmac.new(secret_key.encode("utf-8"), password.encode("utf-8"), hashlib.sha256).hexdigest()
        assert password_service.hash_password(password) == expected

    def test_hash_handles_unicode_password(self, password_service: PasswordService) -> None:
        """Unicode passwords should hash without raising."""
        assert len(password_service.hash_password("pässwörd-😀")) == 64


class TestCheckPassword:
    """Test ``PasswordService.check_password``."""

    def test_check_returns_true_for_matching_password(self, password_service: PasswordService) -> None:
        """A password matches its own stored digest."""
        hashed = password_service.hash_password("password")
        assert password_service.check_password("password", hashed) is True

    def test_check_returns_false_for_wrong_password(self, password_service: PasswordService) -> None:
        """A different password must not validate against the digest."""
        hashed = password_service.hash_password("password")
        assert password_service.check_password("wrong-password", hashed) is False

    def test_check_returns_false_for_modified_hash(self, password_service: PasswordService) -> None:
        """A tampered digest must not validate."""
        hashed = password_service.hash_password("password")
        tampered = "0" * 64 if hashed != "0" * 64 else "1" * 64
        assert password_service.check_password("password", tampered) is False

    def test_check_is_case_sensitive(self, password_service: PasswordService) -> None:
        """Hashing is case-sensitive in the password input."""
        hashed = password_service.hash_password("Password")
        assert password_service.check_password("password", hashed) is False
