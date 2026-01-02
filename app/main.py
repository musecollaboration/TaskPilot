from fastapi import FastAPI

from app.auth.auth_handlers import router as auth_router
from app.handlers.admin_todo_items import router as admin_todo_item_router
from app.handlers.todo_item import router as todo_item_router
from app.handlers.user import router as user_router
from app.settings import settings


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    openapi_url=f"{settings.API_VERSION_PREFIX}/openapi.json",
    docs_url=f"{settings.API_VERSION_PREFIX}/docs",
    redoc_url=f"{settings.API_VERSION_PREFIX}/redoc",
)


@app.get("/")
async def root():
    """Информация о приложении."""
    return {
        "message": "Добро пожаловать в приложение",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }

app.include_router(user_router, prefix=settings.API_VERSION_PREFIX)
app.include_router(admin_todo_item_router, prefix=settings.API_VERSION_PREFIX)
app.include_router(auth_router, prefix=settings.API_VERSION_PREFIX)
app.include_router(todo_item_router, prefix=settings.API_VERSION_PREFIX)
