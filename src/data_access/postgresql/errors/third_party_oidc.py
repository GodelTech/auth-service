class ThirdPartyStateNotFoundError(Exception):
    """Use this class when the database does not contain the state you are looking for"""


class ThirdPartyStateDuplicationError(Exception):
    """Use this class when the database already contains the state you are trying to create"""