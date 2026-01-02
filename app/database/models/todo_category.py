from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy.dialects.postgresql import ENUM as SAEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.database.models.enums import CategoryName


if TYPE_CHECKING:
    from app.database.models.todo_item import TodoItem


class TodoCategory(Base):
    __tablename__ = "todo_categories"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
        type_=PGUUID(as_uuid=True)
    )
    name: Mapped['CategoryName'] = mapped_column(
        default=CategoryName.personal,
        nullable=False,
        type_=SAEnum(CategoryName)
    )

    items: Mapped[list['TodoItem']] = relationship(
        "TodoItem",
        back_populates="category",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"TodoCategory(id={self.id}, name={self.name})"
