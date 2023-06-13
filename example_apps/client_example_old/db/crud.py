from sqlalchemy.orm import Session

from client_example.api import schemas
from client_example.db import models


def create_user_note(
    db: Session, item: schemas.RequestNoteCreate, user_id: int
):
    db_item = models.Note(**item.dict(), user_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_notes(db: Session, skip: int, limit: int, user_id: int):
    return (
        db.query(models.Note)
        .filter(models.Note.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_note(db: Session, id: int):
    return db.query(models.Note).filter(models.Note.id == id).first()
