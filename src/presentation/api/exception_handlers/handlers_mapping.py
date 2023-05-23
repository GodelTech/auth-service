from jwt import DecodeError

from src.data_access.postgresql.errors import ClientNotFoundError, ClientPostLogoutRedirectUriError, \
    ClientRedirectUriError, ClientScopesError, ThirdPartyStateDuplicationError, UserCodeNotFoundError, \
    UserNotFoundError, WrongDataError, WrongPasswordError, WrongResponseTypeError
from src.data_access.postgresql.errors.persistent_grant import PersistentGrantNotFoundError
from .client_not_found_error_handler import client_not_found_error_handler
from .client_post_logout_redirect_uri_error_handler import client_post_logout_redirect_uri_error_handler
from .client_redirect_uri_error_handler import client_redirect_uri_error_handler
from .client_scopes_error_handler import client_scopes_error_handler
from .decode_error_handler import decode_error_handler
from .persistent_grant_not_found_error_handler import persistent_grant_not_found_error_handler
from .third_party_state_duplication_error_handler import third_party_state_duplication_error_handler
from .user_code_not_found_error_handler import user_code_not_found_error_handler
from .user_not_found_error_handler import user_not_found_error_handler
from .wrong_data_error_handler import wrong_data_error_handler
from .wrong_password_error_handler import wrong_password_error_handler
from .wrong_response_type_error_handler import wrong_response_type_error_handler

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
}
