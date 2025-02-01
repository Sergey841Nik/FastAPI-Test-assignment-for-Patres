from typing import Self

from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    EmailStr,
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
    password: str = Field(description="Пароль в формате HASH-строки")


class UserAuth(EmailModel):
    password: str = Field(
        min_length=5, max_length=50, description="Пароль, от 5 до 50 знаков"
    )

class BooksInfo(BaseModel):
    author: int
    title: str
    description: str
    genre: str
    

class UserInfo(UserBase):
    id: int = Field(description="Идентификатор пользователя")
    books: list[BooksInfo] = Field(description="Список книг")

class UserInfoAll(UserBase):
    id: int = Field(description="Идентификатор пользователя")

