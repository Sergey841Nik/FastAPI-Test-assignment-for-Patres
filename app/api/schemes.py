
from datetime import datetime
from pydantic import BaseModel, EmailStr


class BookUpdateDB(BaseModel):
    title: str | None = None
    description: str | None = None
    author: int | None = None
    genre: str | None = None
    amount: int | None = None

class HandingBookFind(BaseModel):
    book_id: int
    user_id: int

class HandingBookAddDB(HandingBookFind):
    amount: int
    book_return_date: datetime

class UserInfo(BaseModel):
    last_name: str
    first_name: str
    email: EmailStr

class BooksInfo(BookUpdateDB):
    id: int
    users: list[UserInfo]
    