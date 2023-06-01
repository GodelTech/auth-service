from jwt import DecodeError
from sqlalchemy import exc
from src.data_access.postgresql.errors import (
    ClientNotFoundError,
    ClientPostLogoutRedirectUriError,
    ClientRedirectUriError,
    ClientScopesError,
    ThirdPartyStateDuplicationError,
    UserCodeNotFoundError,
    TokenIncorrectError,
    GrantNotFoundError,
    ClaimsNotFoundError,
    UserNotFoundError,
    WrongDataError,
    WrongPasswordError,
    WrongResponseTypeError,
    IncorrectAuthTokenError,
)
from src.data_access.postgresql.errors.persistent_grant import (
    PersistentGrantNotFoundError,
)
from src.business_logic.third_party_auth.errors import (
    UnsupportedThirdPartyAuthProviderError,
    ThirdPartyAuthInvalidStateError,
    ThirdPartyAuthProviderInvalidRequestDataError,
)
from src.data_access.postgresql.errors.third_party_oidc import ParsingError
from .auth_token_errors_handler import incorrect_token_auth_error_handler
from .base_error_handler import (
    base_bad_request_error_handler,
    base_not_found_error_handler,
)
from .claims_not_found_error_handler import claims_not_found_error_handler
from .client_not_found_error_handler import client_not_found_error_handler
from .client_post_logout_redirect_uri_error_handler import (
    client_post_logout_redirect_uri_error_handler,
)
from .client_redirect_uri_error_handler import (
    client_redirect_uri_error_handler,
)
from .client_scopes_error_handler import client_scopes_error_handler
from .decode_error_handler import decode_error_handler
from .grant_not_found_error_handler import grant_not_found_error_handler
from .incorrect_token_error_handler import incorrect_token_error_handler
from .integrity_error_handler import integryty_error_handler
from .parsing_error_handler import parsing_error_handler
from .persistent_grant_not_found_error_handler import (
    persistent_grant_not_found_error_handler,
)
from .third_party_state_duplication_error_handler import (
    third_party_state_duplication_error_handler,
)
from .user_code_not_found_error_handler import (
    user_code_not_found_error_handler,
)
from .user_not_found_error_handler import user_not_found_error_handler
from .wrong_data_error_handler import wrong_data_error_handler
from .wrong_password_error_handler import wrong_password_error_handler
from .wrong_response_type_error_handler import (
    wrong_response_type_error_handler,
)
from .unsupported_third_party_auth_provider_error_handler import (
    unsupported_third_party_auth_provider_error_handler,
)
from .invalid_state_error_handler import invalid_state_error_handler
from .third_party_auth_provider_invalid_request_data_error_handler import (
    invalid_request_data_error_handler,
)

exception_handler_mapping = {
    ClientNotFoundError: client_not_found_error_handler,
    ClientPostLogoutRedirectUriError: client_post_logout_redirect_uri_error_handler,
    ClientRedirectUriError: client_redirect_uri_error_handler,
    ClientScopesError: client_scopes_error_handler,
    DecodeError: decode_error_handler,
    PersistentGrantNotFoundError: persistent_grant_not_found_error_handler,
    ThirdPartyStateDuplicationError: third_party_state_duplication_error_handler,
    UserCodeNotFoundError: user_code_not_found_error_handler,
    UserNotFoundError: user_not_found_error_handler,
    WrongDataError: wrong_data_error_handler,
    WrongPasswordError: wrong_password_error_handler,
    WrongResponseTypeError: wrong_response_type_error_handler,
    TokenIncorrectError: incorrect_token_error_handler,
    GrantNotFoundError: grant_not_found_error_handler,
    ClaimsNotFoundError: claims_not_found_error_handler,
    IncorrectAuthTokenError: incorrect_token_auth_error_handler,
    KeyError: base_bad_request_error_handler,
    exc.IntegrityError: integryty_error_handler,
    ValueError: base_not_found_error_handler,
    ParsingError: parsing_error_handler,
    UnsupportedThirdPartyAuthProviderError: unsupported_third_party_auth_provider_error_handler,
    ThirdPartyAuthInvalidStateError: invalid_state_error_handler,
    ThirdPartyAuthProviderInvalidRequestDataError: invalid_request_data_error_handler,
}
