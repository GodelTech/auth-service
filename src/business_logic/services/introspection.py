from typing import Any, Optional, TYPE_CHECKING
from fastapi import Request
from jwt.exceptions import ExpiredSignatureError, PyJWTError

from src.data_access.postgresql.errors import TokenIncorrectError
from src.di.providers import provide_jwt_manager
from src.data_access.postgresql.repositories.client import ClientRepository
from src.data_access.postgresql.repositories.persistent_grant import (
    PersistentGrantRepository,
)
from src.data_access.postgresql.repositories.user import UserRepository

from src.presentation.api.models.introspection import (
    BodyRequestIntrospectionModel,
)
from sqlalchemy.ext.asyncio import AsyncSession
# if TYPE_CHECKING:
from src.business_logic.jwt_manager import JWTManager


class IntrospectionService:
    """A class that provides token introspection functionality. It allows authorized
    protected resources to query the authorization server to determine
    the set of metadata for a given token that was presented to them by
    an OAuth 2.0 client. This metadata includes whether the token is curently active or expired,
    and what rights of access it carries. Token introspection allows a protected resource to
    query this information regardless of whether or not it is carried in
    the token itself, allowing this method to be used along with or
    independently of structured token values.

    More detalis about the functionality can be found in the
    [official documentation](https://www.rfc-editor.org/rfc/rfc7662)


    Args:
        session (AsyncSession): The asynchronous session for database operations.
        user_repo (UserRepository): The repository for user-related operations.
        client_repo (ClientRepository): The repository for client-related operations.
        persistent_grant_repo (PersistentGrantRepository): The repository for persistent grant-related operations.
        jwt (JWTService, optional): The JWT service for token decoding. Defaults to JWTService().

    Raises:
        TokenIncorrectError: If the token is incorrect or missing.

    Attributes:
        jwt (JWTService): The JWT service for token decoding.
        request (Optional[Request]): The request object.
        authorization (Optional[str]): The authorization header.
        request_body (Optional[BodyRequestIntrospectionModel]): The introspection request body.
        user_repo (UserRepository): The repository for user-related operations.
        client_repo (ClientRepository): The repository for client-related operations.
        persistent_grant_repo (PersistentGrantRepository): The repository for persistent grant-related operations.
        session (AsyncSession): The asynchronous session for database operations.
    """

    def __init__(
        self,
        session: AsyncSession,
        user_repo: UserRepository,
        client_repo: ClientRepository,
        persistent_grant_repo: PersistentGrantRepository,
        jwt: JWTManager = provide_jwt_manager(),
    ) -> None:
        self.jwt = jwt
        self.request: Optional[Request] = None
        self.authorization: Optional[str] = None
        self.request_body: Optional[BodyRequestIntrospectionModel] = None
        self.user_repo = user_repo
        self.client_repo = client_repo
        self.persistent_grant_repo = persistent_grant_repo
        self.session = session

    async def analyze_token(self) -> dict[str, Any]:
        """Analyzes the token and returns the introspection response as a dictionary.


        More detalis about the functionality can be found in the
        [official documentation](https://www.rfc-editor.org/rfc/rfc7662#section-2.2)


        Returns:
            dict[str, Any]: The introspection response. The result dictionary contains required parameter
            "active" which contains information about whether the presented token is active. can contain many optional parameters:
            scope - a string containing a space-separated list of scopes associated with this token,
            client_id - client identifier for the OAuth 2.0 client that requested this token,
            username - human-readable identifier for the resource owner who authorized this token,
            token_type - type of the supplied token,
            exp - timestamp indicating when will the token expire,
            iat - timestamp indicating when the token was issued,
            nbf - timestamp indicating when this token is not to be used before,
            sub - subject of the token, usually a machine-readable identifier of the resource owner who
            authorized this token.
            aud - service-specific string identifier or list of string identifiers representing the intended
            audience for this token,
            iss - string representing the issuer of this token,
            jti - string identifier for the token.

        Raises:
            TokenIncorrectError: If the token is incorrect or missing.
        """
        if self.request_body is None:
            raise TokenIncorrectError

        decoded_token = {}
        response: dict[str, Any] = {}

        try:
            decoded_token = await self.jwt.decode(
                token=self.request_body.token, audience="introspection"
            )
        except ExpiredSignatureError:
            return {"active": False}
        except PyJWTError:
            raise TokenIncorrectError

        if self.request_body.token_type_hint in (
            "access-token",
            "access_token",
            "access",
            "authorization_code",
            "authorization-code",
        ):
            response["active"] = True

        if not response:
            if self.request_body.token_type_hint is None:
                # If token type hint is not provided, check all grant types for the token
                list_of_types = [
                    token_type[0]
                    for token_type in await self.persistent_grant_repo.get_all_types()
                ]

                for token_type in list_of_types:
                    if await self.persistent_grant_repo.exists(
                        grant_type=token_type,
                        grant_data=self.request_body.token,
                    ):
                        # If the token exists for a grant type, update the token type hint and set the response as active
                        self.request_body.token_type_hint = token_type
                        response = {"active": True}
                        break
            else:
                # Check if the token exists for the provided token type hint
                exists = await self.persistent_grant_repo.exists(
                    grant_type=self.request_body.token_type_hint,
                    grant_data=self.request_body.token,
                )
                response = {"active": exists}

        if response.get("active"):
            # If response is "active", get other available parameters
            response["iss"] = self.slice_url()
            response["token_type"] = self.get_token_type()
            response["username"] = await self.get_username(decoded_token)

            for parameter in (
                "sub",
                "exp",
                "iat",
                "client_id",
                "jti",
                "aud",
                "nbf",
                "scope",
            ):
                try:
                    response[parameter] = decoded_token.get(parameter)
                except:
                    pass

        return response

    def get_token_type(self) -> str:
        """A helper method that returns the type of the token.

        Returns:
            str: a token type.
        """
        return "Bearer"

    def slice_url(self) -> str:
        """A helper method that retrieves the issuer from the url.

        Returns:
            str: a string containing the issuer.

        Raises:
            TokenIncorrectError: If the token is incorrect or missing.

        """
        if self.request is None:
            raise TokenIncorrectError
        result = str(self.request.url).rsplit("/", 2)
        return result[0]

    async def get_username(self, decoded_token: dict) -> Optional[str]:
        """A helper method that retrieves the username from the token.

        Returns:
            str: a string containing the username.
        """

        user_id = decoded_token.get("sub")
        if user_id is not None:
            try:
                return await self.user_repo.get_username_by_id(id=int(user_id))
            except:
                pass
        return None
