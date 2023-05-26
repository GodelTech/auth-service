class ThirdPartyAuthBaseException(Exception):
    """Base exception for exceptions related to missing a requested third party provider data in database."""


class ThirdPartyStateNotFoundError(ThirdPartyAuthBaseException):
    """Use this class when the database does not contain the state you are looking for"""


class ThirdPartyStateDuplicationError(ThirdPartyAuthBaseException):
    """Use this class when the database already contains the state you are trying to create"""


class WrongDataError(ThirdPartyAuthBaseException):
    """Use this class when the final third party redirect uri is None"""


class ThirdPartyAuthProviderNameError(ThirdPartyAuthBaseException):
    """Use this class when a provider is not supported."""


class ParsingError(Exception):
    """Use this class when there is an error in parsing"""
