"""Unit tests for ``PasswordService``."""

import bcrypt
import pytest

from expenses_counter.services.auth import PasswordService


class TestHashPassword:
    """Test ``PasswordService.hash_password``."""

    def test_hash_returns_string(self) -> None:
        """The bcrypt digest must be returned as a UTF-8 string."""
        hashed = PasswordService.hash_password("password")
        assert isinstance(hashed, str)

    def test_hash_is_bcrypt_formatted(self) -> None:
        """The digest must follow the standard bcrypt ``$2<algo>$<cost>$...`` layout."""
        hashed = PasswordService.hash_password("password")
        assert hashed.startswith(("$2a$", "$2b$", "$2y$"))
        # bcrypt hashes are always 60 chars in modular crypt format
        assert len(hashed) == 60

    def test_hash_is_non_deterministic(self) -> None:
        """Each call generates a new salt, so digests for the same password differ."""
        first = PasswordService.hash_password("password")
        second = PasswordService.hash_password("password")
        assert first != second

    def test_hash_differs_for_different_passwords(self) -> None:
        """Different inputs must produce different digests."""
        assert PasswordService.hash_password("a") != PasswordService.hash_password("b")

    def test_hash_is_verifiable_with_bcrypt(self) -> None:
        """The digest must validate against ``bcrypt.checkpw`` directly."""
        hashed = PasswordService.hash_password("password")
        assert bcrypt.checkpw(b"password", hashed.encode("utf-8")) is True

    def test_hash_handles_unicode_password(self) -> None:
        """Unicode passwords should hash without raising and remain verifiable."""
        password = "pässwörd-😀"
        hashed = PasswordService.hash_password(password)
        assert PasswordService.check_password(password, hashed) is True

    def test_hash_is_static_method(self) -> None:
        """``hash_password`` is callable without instantiating the service."""
        assert isinstance(PasswordService.hash_password("password"), str)


class TestCheckPassword:
    """Test ``PasswordService.check_password``."""

    def test_check_returns_true_for_matching_password(self) -> None:
        """A password matches its own stored digest."""
        hashed = PasswordService.hash_password("password")
        assert PasswordService.check_password("password", hashed) is True

    def test_check_returns_false_for_wrong_password(self) -> None:
        """A different password must not validate against the digest."""
        hashed = PasswordService.hash_password("password")
        assert PasswordService.check_password("wrong-password", hashed) is False

    def test_check_is_case_sensitive(self) -> None:
        """Verification is case-sensitive in the password input."""
        hashed = PasswordService.hash_password("Password")
        assert PasswordService.check_password("password", hashed) is False

    def test_check_returns_true_for_externally_generated_hash(self) -> None:
        """A hash produced directly by ``bcrypt`` should still validate."""
        hashed = bcrypt.hashpw(b"password", bcrypt.gensalt()).decode("utf-8")
        assert PasswordService.check_password("password", hashed) is True

    def test_check_handles_unicode_password(self) -> None:
        """Unicode passwords round-trip through hash/check correctly."""
        hashed = PasswordService.hash_password("pässwörd-😀")
        assert PasswordService.check_password("pässwörd-😀", hashed) is True
        assert PasswordService.check_password("passwoerd", hashed) is False

    def test_check_rejects_invalid_hash_format(self) -> None:
        """A malformed digest must not raise an unhandled error path silently."""
        with pytest.raises(ValueError):
            PasswordService.check_password("password", "not-a-bcrypt-hash")

    def test_check_is_static_method(self) -> None:
        """``check_password`` is callable without instantiating the service."""
        hashed = PasswordService.hash_password("password")
        assert PasswordService.check_password("password", hashed) is True
