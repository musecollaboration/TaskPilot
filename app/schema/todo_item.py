from datetime import date, datetime
from typing import Annotated
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from app.database.models.enums import CategoryName


class TodoItemBase(BaseModel):
    title: Annotated[str, Field(max_length=100)]
    description: Annotated[str | None, Field(max_length=500)] = None
    date_of_execution: Annotated[date | None, Field(default=None)] = None
    category_name: Annotated[CategoryName, Field(default=CategoryName.personal)]



class TodoItemCreate(TodoItemBase):
    pass


class TodoItemUpdate(BaseModel):
    title: Annotated[str | None, Field(max_length=100, default=None)]
    description: Annotated[str | None, Field(max_length=500, default=None)]
    completed: Annotated[bool | None, Field(default=None)]
    date_of_execution: Annotated[date | None, Field(default=None)]
    category_name: Annotated[CategoryName | None, Field(default=None)]


class TodoItemRead(TodoItemBase):
    model_config = ConfigDict(from_attributes=True)

    created_at: Annotated[datetime, Field(default_factory=datetime.now)]
    updated_at: Annotated[datetime | None, Field(default=None)]
    completed: Annotated[bool, Field(default=False)]
    id: Annotated[UUID, Field]
    user_id: Annotated[UUID, Field]
