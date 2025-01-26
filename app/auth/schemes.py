from typing import Self

from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    EmailStr,
    computed_field,
    model_validator,
)

from .utils import hash_password


class EmailModel(BaseModel):
    email: EmailStr = Field(description="Электронная почта")
    model_config = ConfigDict(from_attributes=True)


class UserBase(EmailModel):
    first_name: str = Field(
        min_length=3, max_length=50, description="Имя, от 3 до 50 символов"
    )
    last_name: str = Field(
        min_length=3, max_length=50, description="Фамилия, от 3 до 50 символов"
    )


class UserRegister(UserBase):
    password: str = Field(
        min_length=5, max_length=50, description="Пароль, от 5 до 50 знаков"
    )
    confirm_password: str = Field(
        min_length=5, max_length=50, description="Повторите пароль"
    )

    @model_validator(mode="after")
    def check_password(self) -> Self:
        if self.password != self.confirm_password:
            raise ValueError("Пароли не совпадают")
        self.password = hash_password(
            self.password
        )  # хешируем пароль до сохранения в базе данных
        return self


class UserAddDB(UserBase):
    password: bytes = Field(description="Пароль в формате HASH-строки")


class UserAuth(EmailModel):
    password: str = Field(
        min_length=5, max_length=50, description="Пароль, от 5 до 50 знаков"
    )

class ChangeUserRole(EmailModel):
    role_id: int = Field(description="Идентификатор роли")


class RoleModel(BaseModel):
    id: int = Field(description="Идентификатор роли")
    name: str = Field(description="Название роли")
    model_config = ConfigDict(from_attributes=True)

class RoleAddDB(BaseModel):
    name: str = Field(description="Название роли")


class UserInfo(UserBase):
    id: int = Field(description="Идентификатор пользователя")
    role: RoleModel = Field(exclude=True)

    @computed_field
    def role_name(self) -> str:
        return self.role.name

    @computed_field
    def role_id(self) -> int:
        return self.role.id
