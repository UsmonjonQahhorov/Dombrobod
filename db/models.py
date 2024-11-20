from datetime import datetime

from sqlalchemy import Column, String, Sequence, Boolean, Integer, Float, DateTime, ForeignKey
from sqlalchemy import Integer, String, BigInteger, VARCHAR, ForeignKey, Text
from sqlalchemy.future import select
from sqlalchemy.orm import relationship, mapped_column, Mapped

from db import Base
from db.utils import CreatedModel, db, AbstractClass


class Users(CreatedModel):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(255))
    phone_number: Mapped[str] = mapped_column(String(255))
    username: Mapped[str] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_admin: Mapped[bool] = mapped_column(default=False)


class Groups(CreatedModel):
    __tablename__ = 'groups'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group_id: Mapped[str] = mapped_column(String(255))
    username: Mapped[str] = mapped_column(String(255))

    def __repr__(self):
        return f"{self.group_id, self.username, self.id}"


class Messages(CreatedModel):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    message_id: Mapped[int] = mapped_column(Integer)
    schedule: Mapped[str] = mapped_column(String(255))
    group_id = Column(Integer, ForeignKey("groups.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    job_name = Column(String(255))
