from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr


class UserBase(BaseModel):
    username: Annotated[str, Field(
        min_length=3,
        max_length=50,
        description='Имя пользователя (от 3 до 50 символов)')
    ]
    email: Annotated[EmailStr, Field(
        description='Электронная почта пользователя')
    ]


class UserCreate(UserBase):
    password: Annotated[SecretStr, Field(
        min_length=8,
        max_length=50,
        description='Пароль пользователя (от 8 до 50 символов)')
    ]


class UserUpdate(UserBase):
    username: Annotated[str | None, Field(
        min_length=3,
        max_length=50,
        description='Имя пользователя (от 3 до 50 символов)',
        default=None)
    ]
    password: Annotated[SecretStr | None, Field(
        min_length=8,
        max_length=50,
        description='Пароль пользователя (от 4 до 50 символов)',
        default=None)
    ]
    email: Annotated[EmailStr | None, Field(
        description='Электронная почта пользователя',
        default=None)
    ]


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: Annotated[UUID, Field]
