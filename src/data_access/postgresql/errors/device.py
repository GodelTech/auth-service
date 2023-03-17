class DeviceBaseException(Exception):
    """Base exception for exceptions related to missing a requested device data in database."""


class UserCodeNotFoundError(DeviceBaseException):
    """Use this class when the database does not contain the user code you are looking for"""


class DeviceRegistrationError(DeviceBaseException):
    """Use this class when a device registration process is not finished"""


class DeviceCodeNotFoundError(DeviceBaseException):
    """Use this class when the database does not contain the device code you are looking for"""


class DeviceCodeExpirationTimeError(DeviceBaseException):
    """Use this class when the device code you are looking has already expired"""
