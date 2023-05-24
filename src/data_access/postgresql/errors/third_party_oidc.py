class ThirdPartyStateNotFoundError(Exception):
    """Use this class when the database does not contain the state you are looking for"""


class ThirdPartyStateDuplicationError(Exception):
    """Use this class when the database already contains the state you are trying to create"""


class WrongDataError(Exception):
    """Use this class when the final third party redirect uri is None"""


class ParsingError(Exception):
    """Use this class when there is an error in parsing"""
