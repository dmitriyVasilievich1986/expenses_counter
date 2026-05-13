"""Unit tests for ``JWTTokenService``."""

from datetime import datetime, timedelta, timezone

import jwt
import pytest
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError, PyJWTError

from expenses_counter.services.auth import JWTTokenService
from expenses_counter.services.auth.models import AccessToken, JWTTokenMetadata


@pytest.fixture
def secret_key() -> str:
    """Return a stable JWT signing key for tests.

    The key is intentionally long enough (>= 32 bytes for HS256, >= 64 bytes
    for HS512) to satisfy ``pyjwt``'s key-length recommendations and avoid
    warnings in the test output.

    Returns:
        str: Secret key used to sign and verify tokens.

    """
    return "test-jwt-secret-with-enough-length-for-hs512-algorithm-padding-padding"


@pytest.fixture
def jwt_service(secret_key: str) -> JWTTokenService:
    """Return a ``JWTTokenService`` built from the test secret key.

    Args:
        secret_key: Signing secret used by the service.

    Returns:
        JWTTokenService: Configured service ready to issue tokens.

    """
    return JWTTokenService(secret_key)


class TestJWTTokenServiceInit:
    """Test ``JWTTokenService.__init__``."""

    def test_defaults_to_hs256(self, secret_key: str) -> None:
        """The default algorithm should be HS256."""
        service = JWTTokenService(secret_key)
        assert service.algorithm == "HS256"
        assert service.secret_key == secret_key

    def test_accepts_custom_algorithm(self, secret_key: str) -> None:
        """A caller-provided algorithm should be retained."""
        service = JWTTokenService(secret_key, algorithm="HS512")
        assert service.algorithm == "HS512"


class TestGenerateToken:
    """Test ``JWTTokenService.generate_token``."""

    def test_returns_access_token_model(self, jwt_service: JWTTokenService) -> None:
        """The result must be an ``AccessToken`` with a non-empty token string."""
        access_token = jwt_service.generate_token(user_id=42)
        assert isinstance(access_token, AccessToken)
        assert isinstance(access_token.token, str)
        assert access_token.token  # non-empty

    def test_expiration_is_about_one_day(self, jwt_service: JWTTokenService) -> None:
        """The token expiration should be ~1 day in the future."""
        before = datetime.now(timezone.utc)
        access_token = jwt_service.generate_token(user_id=42)
        after = datetime.now(timezone.utc)

        # expires_at should be in [before + 1d, after + 1d]
        assert before + timedelta(days=1) <= access_token.expires_at <= after + timedelta(days=1)

    def test_payload_embeds_user_id_and_exp(self, jwt_service: JWTTokenService, secret_key: str) -> None:
        """The encoded JWT must carry the user_id and exp claims."""
        access_token = jwt_service.generate_token(user_id=42)
        payload = jwt.decode(access_token.token, secret_key, algorithms=["HS256"])
        assert payload["user_id"] == 42
        assert "exp" in payload

    def test_signed_with_configured_algorithm(self, secret_key: str) -> None:
        """The token's ``alg`` header should match the configured algorithm."""
        service = JWTTokenService(secret_key, algorithm="HS512")
        token = service.generate_token(user_id=1).token
        header = jwt.get_unverified_header(token)
        assert header["alg"] == "HS512"


class TestDecodeToken:
    """Test ``JWTTokenService.decode_token``."""

    def test_decodes_valid_token(self, jwt_service: JWTTokenService) -> None:
        """A freshly issued token should decode back to matching metadata."""
        access_token = jwt_service.generate_token(user_id=42)
        metadata = jwt_service.decode_token(access_token.token)

        assert isinstance(metadata, JWTTokenMetadata)
        assert metadata.user_id == 42
        # Datetimes round-trip via integer timestamps, so compare within 1 second.
        assert abs((metadata.exp - access_token.expires_at).total_seconds()) < 1

    def test_raises_on_expired_token(self, jwt_service: JWTTokenService, secret_key: str) -> None:
        """An expired token should raise ``ExpiredSignatureError``."""
        expired_at = datetime.now(timezone.utc) - timedelta(hours=1)
        expired_token = jwt.encode(
            {"user_id": 1, "exp": expired_at},
            secret_key,
            algorithm="HS256",
        )

        with pytest.raises(ExpiredSignatureError):
            jwt_service.decode_token(expired_token)

    def test_raises_on_wrong_signature(self, jwt_service: JWTTokenService) -> None:
        """A token signed with a different key should raise an ``InvalidSignatureError``."""
        bad_token = jwt.encode(
            {"user_id": 1, "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
            "different-key-with-enough-padding-to-pass-length-requirements",
            algorithm="HS256",
        )
        with pytest.raises(InvalidSignatureError):
            jwt_service.decode_token(bad_token)

    def test_raises_on_malformed_token(self, jwt_service: JWTTokenService) -> None:
        """A non-JWT string should raise a ``PyJWTError`` subclass."""
        with pytest.raises(PyJWTError):
            jwt_service.decode_token("not-a-jwt")

    def test_can_skip_signature_verification(self, jwt_service: JWTTokenService) -> None:
        """``verify_signature=False`` should accept tokens signed by another key."""
        foreign_token = jwt.encode(
            {"user_id": 7, "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
            "different-key-with-enough-padding-to-pass-length-requirements",
            algorithm="HS256",
        )
        metadata = jwt_service.decode_token(foreign_token, verify_signature=False)
        assert metadata.user_id == 7


class TestRoundTrip:
    """End-to-end round-trip between encode and decode."""

    def test_generate_then_decode_preserves_user_id(self, jwt_service: JWTTokenService) -> None:
        """Generating and decoding should produce the same ``user_id`` for many ids."""
        for user_id in (1, 2, 100, 999999):
            metadata = jwt_service.decode_token(jwt_service.generate_token(user_id).token)
            assert metadata.user_id == user_id
