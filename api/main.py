import sqlalchemy.exc
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from pydantic.schema import List
from sqlalchemy.orm import Session
import uvicorn
from starlette import status

import crud
import models
import schemas
from database import SessionLocal, engine

app = FastAPI(title="User Note Service")


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db = SessionLocal()
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response


# Dependency
def get_db(request: Request):
    return request.state.db


@app.get("/")
async def handle_root():
    return RedirectResponse("/docs")


@app.post("/users/", response_model=schemas.User)
def create_user(user_obj: schemas.UserIn, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, user_obj.email):
        raise HTTPException(status_code=400, detail="Duplicate user email")
    return crud.create_user(db=db, user=user_obj)


@app.get("/users/", response_model=List[schemas.User])
def search_users(search_str: str, db: Session = Depends(get_db)):
    return crud.search_users(db, search_str)


@app.get("/users/{user_id}", response_model=schemas.User)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user_obj = crud.get_user_by_id(db, user_id)
    if not user_obj:
        raise HTTPException(status_code=404, detail="user id not found")

    return user_obj


@app.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user: schemas.UserIn, db: Session = Depends(get_db)):
    user_obj = crud.update_user(db, user_id, user)
    if not user_obj:
        raise HTTPException(status_code=404, detail="user id not found")

    return user_obj


@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user id not found")

    return {"status": "deleted"}


@app.get("/users/{user_id}/notes", response_model=List[schemas.Note])
def get_user_notes(user_id: int, db: Session = Depends(get_db)):
    notes = crud.get_notes(db, user_id)
    return notes


@app.post("/users/{user_id}/notes", response_model=schemas.Note)
def add_user_note(user_id: int, note: schemas.NoteIn, db: Session = Depends(get_db)):
    try:
        note_obj = crud.add_note(db, user_id, note)
        return note_obj
    except sqlalchemy.exc.DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user id not found")


@app.put("/users/{user_id}/notes/{note_id}", response_model=schemas.Note)
def update_user_note(user_id: int, note_id: int, note: schemas.NoteIn, db: Session=Depends(get_db)):
    try:
        note_obj = crud.update_note(db, user_id, note_id, note)
        return note_obj
    except sqlalchemy.exc.DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user or note id not found")


@app.delete("/users/{user_id}/notes/{note_id}")
def delete_user_note(user_id: int, note_id, db: Session = Depends(get_db)):
    deleted = crud.delete_note(db, user_id, note_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="note not found")

    return {"status": "deleted"}


if __name__ == "__main__":
    models.Base.metadata.create_all(bind=engine)
    uvicorn.run(app, host="0.0.0.0", port=8080)
