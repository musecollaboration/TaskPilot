from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.auth.auth_dependencies import get_admin_user
from app.database.dependencies import get_todo_item_service
from app.database.models.todo_item import TodoItem
from app.database.models.user import User
from app.schema.todo_item import TodoItemRead
from app.service.todo_item import TodoItemService


router = APIRouter(
    tags=["admin"],
    prefix="/admin",
)


@router.get(
    "/todo_items",
    response_model=List[TodoItemRead],
    status_code=200
)
async def get_todo_items(
    admin_user: Annotated[User, Depends(get_admin_user)],
    service_todo_item: Annotated[TodoItemService, Depends(get_todo_item_service)],
    user_id: Annotated[UUID, Query(description="ID пользователя")],
) -> List[TodoItem]:
    """
    Получить все элементы списка дел для администратора.
    """
    return await service_todo_item.get_todo_items(
        user_id=user_id
    )
