from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends

from app.auth.auth_dependencies import get_current_user
from app.database.dependencies import get_todo_item_service
from app.database.models.todo_item import TodoItem
from app.database.models.user import User
from app.schema.todo_item import TodoItemCreate, TodoItemRead, TodoItemUpdate
from app.service.todo_item import TodoItemService


router = APIRouter(
    tags=["todo_items"],
    prefix="/todo_items",
)


@router.get(
    "/all",
    response_model=List[TodoItemRead],
    status_code=200
)
async def get_todo_items(
    auth_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[TodoItemService, Depends(get_todo_item_service)]
) -> List[TodoItem]:
    """
    Эндпоинт для получения всех элементов списка дел пользователя.
    Доступно только для аутентифицированных пользователей.
    """
    return await service.get_todo_items(
        user_id=auth_user.id
    )


@router.post(
    "/",
    response_model=TodoItemRead,
    status_code=201
)
async def create_todo_item(
    auth_user: Annotated[User, Depends(get_current_user)],
    todo_item_schema: TodoItemCreate,
    service: Annotated[TodoItemService, Depends(get_todo_item_service)]
) -> TodoItem:
    """
    Эндпоинт для создания элемента списка дел.
    Доступно только для аутентифицированных пользователей.
    """
    return await service.create_todo_item(
        schema=todo_item_schema,
        user_id=auth_user.id
    )


@router.get(
    "/{todo_item_id}",
    response_model=TodoItemRead,
    status_code=200
)
async def get_todo_item(
    auth_user: Annotated[User, Depends(get_current_user)],
    todo_item_id: UUID,
    service: Annotated[TodoItemService, Depends(get_todo_item_service)]
) -> TodoItem:
    """
    Эндпоинт для получения элемента списка дел по идентификатору.
    Доступно только для аутентифицированных пользователей.
    """
    return await service.get_todo_item(
        todo_item_id=todo_item_id,
        user_id=auth_user.id
    )


@router.patch(
    "/{todo_item_id}",
    response_model=TodoItemRead,
    status_code=200
)
async def update_todo_item(
    auth_user: Annotated[User, Depends(get_current_user)],
    todo_item_id: UUID,
    todo_item_schema: TodoItemUpdate,
    service: Annotated[TodoItemService, Depends(get_todo_item_service)]
) -> TodoItem:
    """
    Эндпоинт для обновления элемента списка дел.
    Доступно только для аутентифицированных пользователей.
    """
    return await service.update_todo_item(
        todo_item_id=todo_item_id,
        schema=todo_item_schema,
        user_id=auth_user.id
    )


@router.delete(
    "/{todo_item_id}",
    status_code=200
)
async def delete_todo_item(
    auth_user: Annotated[User, Depends(get_current_user)],
    todo_item_id: UUID,
    service: Annotated[TodoItemService, Depends(get_todo_item_service)]
) -> dict[str, str]:
    """
    Эндпоинт для удаления элемента списка дел.
    Доступно только для аутентифицированных пользователей.
    """
    await service.delete_todo_item(
        todo_item_id=todo_item_id,
        user_id=auth_user.id
    )
    return {"detail": "Элемент списка дел успешно удален"}
