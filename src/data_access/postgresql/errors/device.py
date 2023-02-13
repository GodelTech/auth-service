class UserCodeNotFoundError(Exception):
    """Use this class when the database does not contain the user code you are looking for"""


class DeviceRegistrationError(Exception):
    """Use this class when a device registration process is not finished"""


class DeviceCodeNotFoundError(Exception):
    """Use this class when the database does not contain the device code you are looking for"""


class DeviceCodeExpirationTimeError(Exception):
    """Use this class when the device code you are looking has already expired"""

