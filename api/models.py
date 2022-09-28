from sqlalchemy import Boolean, Column, ForeignKey, Integer, Float, String, DateTime, func
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), index=True)
    email = Column(String(255), unique=True)


class Note(Base):
    __tablename__ = "note"

    id = Column(Integer, primary_key=True)
    content = Column(String(255))
    created_at = Column(DateTime, nullable=False, server_default=func.current_timestamp())
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="notes", cascade="all, delete")


User.notes = relationship("Note", back_populates="user")
