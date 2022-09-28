from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserIn(BaseModel):
    name: str = Field(example="Vincent Biz", max_length=255)
    email: EmailStr = Field(example="vincent@factory.biz")

    class Config:
        orm_mode = True


class User(UserIn):
    id: int = Field(example=1234)


class NoteIn(BaseModel):
    content: str = Field(example="Remember this!", max_length=255)

    class Config:
        orm_mode = True


class Note(NoteIn):
    id: int = Field(example=321)
    user_id: int = Field(example=1234)
    created_at: datetime = Field(example="2022-09-28T04:59:59.036Z")
