from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from client_example import crud
from client_example.database import get_db
from client_example.schemas import RequestNoteCreate, ResponseNote
from client_example.utils import (
    get_current_user,
    get_identity_server_public_key,
    is_token_valid_test,
)

router = APIRouter(prefix="/notes", tags=['Notes'])


@router.get("/", response_model=List[ResponseNote])
async def get_notes(
    # request: Request,
    limit: int = 10,
    skip: int = 0,
    # current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # public_key = get_identity_server_public_key()
    # access_token = request.headers.get('Authorization').split(" ")[-1]

    # if not is_token_valid_test(access_token, public_key):
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    notes = crud.get_notes(db, skip, limit)
    if notes is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You do not have any notes.",
        )

    return notes


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_notes(
    request_body: RequestNoteCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return crud.create_user_note(
        db=db, item=request_body, user_id=current_user['sub']
    )


@router.get("/{id}/", response_model=ResponseNote)
async def get_note(
    id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    note = crud.get_note(db, id)

    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found.",
        )
    if note.user_id != int(current_user['sub']):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action.",
        )
    return note
