from typing import List

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

import models
import schemas


def create_user(db: Session, user: schemas.UserIn) -> models.User:
    user_obj = models.User(name=user.name, email=user.email)
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj


def get_user_by_email(db: Session, email: str) -> models.User:
    return db.query(models.User).filter(models.User.email == email).first()


def search_users(db: Session, search: str) -> List[models.User]:
    condition = f"%{search}%"
    return db.query(models.User).filter(or_(models.User.name.like(condition), models.User.email.like(condition))).all()


def get_user_by_id(db: Session, user_id: int) -> models.User:
    return db.query(models.User).filter(models.User.id == user_id).first()


def update_user(db: Session, user_id: int, user: schemas.UserIn) -> models.User:
    user_obj = db.query(models.User).filter(models.User.id == user_id).first()
    user_obj.name, user_obj.email = user.name, user.email
    db.commit()
    return user_obj


def delete_user(db: Session, user_id: int) -> bool:
    result = db.query(models.User).filter(models.User.id == user_id).delete()
    db.commit()
    return result > 0


def get_notes(db: Session, user_id: int) -> List[models.Note]:
    notes = db.query(models.Note).filter(models.Note.user_id == user_id).all()
    return notes


def add_note(db: Session, user_id: int, note: schemas.NoteIn) -> models.Note:
    note_obj = models.Note(content=note.content, user_id=user_id)
    db.add(note_obj)
    db.commit()
    db.refresh(note_obj)
    return note_obj


def update_note(db: Session, user_id: int, note_id: int, note: schemas.NoteIn) -> models.Note:
    note_obj = db.query(models.Note).filter(models.Note.user_id == user_id, models.Note.id == note_id).one()
    note_obj.content = note.content
    db.commit()
    return note_obj


def delete_note(db: Session, user_id: int, note_id: int) -> bool:
    result = db.query(models.Note).filter(models.Note.user_id == user_id, models.Note.id == note_id).delete()
    db.commit()
    return result > 0

