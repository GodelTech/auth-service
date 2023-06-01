from fastapi import Form
from pydantic import BaseModel


class ThirdPartyAccessTokenRequestModel(BaseModel):
    """
    Model representing a GET method request model for a third-party access token.

    Attributes:
        code (str): The authorization code.
        state (str): The state parameter.
        grant_type (str): The grant type (default: "authorization_code").

    """

    code: str
    state: str
    grant_type: str = "authorization_code"

    class Config:
        orm_mode = True

    def __repr__(self) -> str:
        return f"Model {self.__class__.__name__}"


class StateRequestModel(BaseModel):
    """
    Model representing a POST method request model with a state parameter.

    Attributes:
        state (str): The state parameter.
    """

    state: str

    @classmethod
    def as_form(cls, state: str = Form(...)) -> "StateRequestModel":
        """
        Creates an instance of the model from form data.

        Args:
            state (str): The state parameter obtained from a form.

        Returns:
            StateRequestModel: An instance of the StateRequestModel.
        """
        return cls(state=state)
