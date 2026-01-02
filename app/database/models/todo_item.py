from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


if TYPE_CHECKING:
    from app.database.models.todo_category import TodoCategory
    from app.database.models.user import User


class TodoItem(Base):
    __tablename__ = "todo_items"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
        type_=PGUUID(as_uuid=True)
    )
    title: Mapped[str] = mapped_column(String, nullable=False, unique=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, onupdate=datetime.now, nullable=True)
    date_of_execution: Mapped[date] = mapped_column(Date, nullable=True)

    category_id: Mapped[UUID] = mapped_column(
        ForeignKey("todo_categories.id",
                   ondelete="CASCADE",
                   onupdate="CASCADE"),
        nullable=False
    )
    category: Mapped["TodoCategory"] = relationship("TodoCategory", back_populates="items")

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id",
                   ondelete="CASCADE",
                   onupdate="CASCADE"),
        nullable=False
    )
    user: Mapped["User"] = relationship("User", back_populates="todo_items")

    def __repr__(self):
        category_name = self.category.name if self.category else None
        return f"TodoItem(id={self.id}, title={self.title}, category_name={category_name})"
