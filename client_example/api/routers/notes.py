from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from client_example.api.schemas import RequestNoteCreate, ResponseNote
from client_example.db import crud
from client_example.db.database import get_db
from client_example.utils import get_user_id

router = APIRouter(prefix="/notes", tags=["Notes"])


@router.get("/", response_model=List[ResponseNote])
async def get_notes(
    limit: int = 10,
    skip: int = 0,
    user_id: int = Depends(get_user_id),
    db: Session = Depends(get_db),
):
    notes = crud.get_notes(db, skip, limit, user_id)
    if notes is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {user_id} does not have any notes",
        )

    return notes


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_notes(
    request_body: RequestNoteCreate,
    user_id: int = Depends(get_user_id),
    db: Session = Depends(get_db),
):
    return crud.create_user_note(db=db, item=request_body, user_id=user_id)


@router.get("/{id}/", response_model=ResponseNote)
async def get_note(
    id: int,
    user_id: int = Depends(get_user_id),
    db: Session = Depends(get_db),
):
    note = crud.get_note(db, id)

    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} was not found.",
        )
    if note.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action.",
        )
    return note
