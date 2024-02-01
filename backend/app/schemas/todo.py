from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class TodoCreate(BaseModel):
    title: str = Field(..., title="Title", max_length=55, min_length=1)
    description: str = Field(..., title="Description", max_length=500, min_length=1)
    status: bool | None = False


class TodoUpdate(BaseModel):
    title: str | None = Field(..., title="Title", max_length=55, min_length=1)
    description: str | None = Field(
        ..., title="Description", max_length=500, min_length=1
    )
    status: bool | None = False


class TodoOut(BaseModel):
    todo_id: UUID
    status: bool
    title: str
    description: str
    created_at: datetime
    created_at: datetime
