from src.presentation.models.authorization import ResponseAuthorizationModel


def get_authorisation(data):
    return ResponseAuthorizationModel(**data)
