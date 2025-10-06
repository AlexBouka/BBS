import jwt
import logging

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jwt.exceptions import InvalidTokenError
from uuid import UUID

from core.config import settings

logger = logging.getLogger(__name__)


class JWTManager:
    def __init__(self):
        self.secret_key = settings.jwt_secret_key
        self.algorithm = settings.jwt_algorithm
        self.access_token_expire_minutes = settings.jwt_access_token_expire_minutes
        self.refresh_token_expire_days = settings.jwt_refresh_token_expire_days

    def create_access_token(
            self, data: Dict[str, Any],
            expires_delta: Optional[timedelta] = None
            ) -> str:
        """
        Creates an access token given the provided data.

        The access token will expire after the given expires_delta if provided, otherwise
        it will expire after the configured access token expire minutes.

        :param data: The data to encode into the access token.
        :param expires_delta: An optional timedelta to specify the access token expiration time.
        :return: The encoded access token as a string.
        """
        to_encode = data.copy()

        # Convert UUID to string for JSON serialization
        if "user_id" in to_encode and isinstance(to_encode["user_id"], UUID):
            to_encode["user_id"] = str(to_encode["user_id"])

        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expire_minutes)

        to_encode.update(
            {
                "exp": expire,
                "iat": datetime.now(timezone.utc),  # Issued at
                "type": "access"
            }
        )
        encoded_jwt: str = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """
        Creates a refresh token given the provided data.

        The refresh token will expire after the configured refresh token expire days.

        :param data: The data to encode into the refresh token.
        :return: The encoded refresh token as a string.
        """
        to_encode = data.copy()

        # Convert UUID to string for JSON serialization
        if "user_id" in to_encode and isinstance(to_encode["user_id"], UUID):
            to_encode["user_id"] = str(to_encode["user_id"])

        expire = datetime.now(timezone.utc) + timedelta(days=self.refresh_token_expire_days)

        to_encode.update(
            {
                "exp": expire,
                "iat": datetime.now(timezone.utc),  # Issued at
                "type": "refresh"
            }
        )
        encoded_jwt: str = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verifies a given token.

        Attempts to decode the token using the configured secret key and algorithm.
        If the token is invalid, logs a warning and returns None.

        :param token: The token to verify.
        :return: The decoded payload if the token is valid, otherwise None.
        :rtype: Optional[Dict[str, Any]]
        """
        try:
            payload: dict = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None

    def is_token_expired(self, token: str) -> bool:
        """
        Checks if a given token has expired.

        If the token is invalid or does not contain an expiration time, returns True.

        :param token: The token to check.
        :return: Whether the token has expired.
        :rtype: bool
        """
        payload = self.verify_token(token)
        if not payload:
            return True

        exp = payload.get("exp")
        if not exp:
            return True

        return datetime.now(timezone.utc) > datetime.fromtimestamp(exp, tz=timezone.utc)


jwt_manager = JWTManager()
