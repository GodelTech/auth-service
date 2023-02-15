from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from client_example.api.routers.auth import client
from client_example.api.schemas import RequestNoteCreate, ResponseNote
from client_example.db import crud
from client_example.db.database import get_db

router = APIRouter(prefix='/notes', tags=['Notes'])


@router.get('/', response_model=List[ResponseNote])
async def get_notes(
    request: Request,
    limit: int = 10,
    skip: int = 0,
    db: Session = Depends(get_db),
):
    token = request.session['access_token']
    user_id = await client.get_id(token)
    notes = crud.get_notes(db, skip, limit, user_id)
    if notes is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User with is {user_id} does not have any notes',
        )

    return notes


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_notes(
    request: Request,
    request_body: RequestNoteCreate,
    db: Session = Depends(get_db),
):
    token = request.session['access_token']
    user_id = await client.get_id(token)
    return crud.create_user_note(db=db, item=request_body, user_id=user_id)


@router.get('/{id}/', response_model=ResponseNote)
async def get_note(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    token = request.session['access_token']
    user_id = await client.get_id(token)
    note = crud.get_note(db, id)

    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'post with id: {id} was not found.',
        )
    if note.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Not authorized to perform requested action.',
        )
    return note
