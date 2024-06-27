from typing import Optional

from litestar import Request

from evidently.ui.components.security import TokenSecurityComponent
from evidently.ui.security.service import SecurityService
from evidently.ui.security.service import User
from evidently.ui.type_aliases import ZERO_UUID

SECRET_HEADER_NAME = "evidently-secret"


default_user = User(id=ZERO_UUID, name="")


class TokenSecurity(SecurityService):
    def __init__(self, config: TokenSecurityComponent):
        self.config = config

    def authenticate(self, request: Request) -> Optional[User]:
        if request.headers.get(SECRET_HEADER_NAME) == self.config.token.get_secret_value():
            return default_user
        return None
