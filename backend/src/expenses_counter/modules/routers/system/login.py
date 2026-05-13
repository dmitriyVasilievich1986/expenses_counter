"""HTTP endpoints for user authentication."""

from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status
from loguru import logger
from sqlalchemy.exc import NoResultFound, SQLAlchemyError

from expenses_counter.config import AppConfig
from expenses_counter.modules.middlewares.dependencies import get_config
from expenses_counter.modules.middlewares.dependencies.daos import get_user_dao
from expenses_counter.modules.routers.schemas.requests.system import LoginBody
from expenses_counter.modules.routers.schemas.responses.system import (
    LoginResponse,
)
from expenses_counter.services.auth import JWTTokenService, PasswordService
from expenses_counter.services.daos import UserDAO

router = APIRouter()


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK, description="Login a user")
async def login(
    body: Annotated[LoginBody, Body(description="The login body")],
    user_dao: Annotated[UserDAO, Depends(get_user_dao)],
    config: Annotated[AppConfig, Depends(get_config)],
) -> LoginResponse:
    """Authenticate a user and return a JWT access token.

    Args:
        body (LoginBody): Username and plaintext password from the client.
        user_dao (UserDAO): DAO used to load the user record by username.
        config (AppConfig): Application configuration (password and JWT secrets).

    Returns:
        LoginResponse: Signed access token and its expiration time.

    Raises:
        HTTPException: If credentials are invalid (401), or a database error
            occurs while loading the user (500).

    """
    try:
        user = await user_dao.get_by_username(body.username)
    except NoResultFound as e:
        logger.warning("User not found")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password") from e
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while retrieving the user", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while retrieving the user",
        ) from e

    password_service = PasswordService(config.services.auth.password_secret_key.get_secret_value())

    if not password_service.check_password(body.password, user.password):
        logger.warning("Invalid username or password")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    jwt_token_service = JWTTokenService(
        secret_key=config.services.auth.jwt_secret_key.get_secret_value(),
        algorithm=config.services.auth.jwt_algorithm,
    )
    access_token = jwt_token_service.generate_token(user.id)

    return LoginResponse(access_token=access_token.token, expires_at=access_token.expires_at)
