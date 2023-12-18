from datetime import datetime
from enum import unique
from uuid import UUID, uuid4
from fastapi_users.db import BeanieBaseUser, BeanieUserDatabase
from pydantic import EmailStr, Field
from beanie import Document, Indexed, Link, before_event, Replace, Insert
from .user import User

from typing_extensions import Annotated



class Todo(Document):
    todo_id: UUID = Field(default_factory=uuid4, unique=True)
    status: bool = False
    title: Indexed(str)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    owner: Link[User]

    @before_event(Replace, Insert)
    def update_updated_at(self):
        self.update_at = datetime.utcnow()

    class Settings:
        name = "todo"