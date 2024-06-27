from litestar.contrib.jwt.jwt_auth import (
    BaseJWTAuth,
    JWTAuth,
    JWTCookieAuth,
    OAuth2Login,
    OAuth2PasswordBearerAuth,
)
from litestar.contrib.jwt.jwt_token import Token
from litestar.contrib.jwt.middleware import (
    JWTAuthenticationMiddleware,
    JWTCookieAuthenticationMiddleware,
)
from litestar.utils import warn_deprecation

__all__ = (
    "BaseJWTAuth",
    "JWTAuth",
    "JWTAuthenticationMiddleware",
    "JWTCookieAuth",
    "JWTCookieAuthenticationMiddleware",
    "OAuth2Login",
    "OAuth2PasswordBearerAuth",
    "Token",
)

warn_deprecation(
    deprecated_name="litestar.contrib.jwt",
    version="2.3.2",
    kind="import",
    removal_in="3.0",
    info="importing from 'litestar.contrib.jwt' is deprecated, please import from 'litestar.security.jwt' instead",
)
