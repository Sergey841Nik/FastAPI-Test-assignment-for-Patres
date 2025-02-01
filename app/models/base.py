from datetime import datetime, timedelta

from sqlalchemy import ForeignKey, String, Text, text, TIMESTAMP, func, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )


class User(Base):
    __tablename__ = "users"

    first_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str]
    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id"), default=1, server_default=text("1")
    )
    role: Mapped["Role"] = relationship("Role", back_populates="users")

    books: Mapped[list["Book"]] = relationship(secondary="handing_books_users", back_populates="users")


    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"


class Role(Base):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    users: Mapped[list["User"]] = relationship(back_populates="role")

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"
    

class Book(Base):
    __tablename__ = "books"
    __table_args__ = (UniqueConstraint("title", "author", name="uq_book"), CheckConstraint('amount >= 0', name='check_amount'))

    title: Mapped[str] = mapped_column(unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text)
    author: Mapped[int] = mapped_column(ForeignKey("authors.id"), nullable=False)
    genre: Mapped[str] = mapped_column(String(20))
    amount: Mapped[int] = mapped_column(default=0, server_default="0")

    users: Mapped[list["User"]] = relationship(
        secondary="handing_books_users", back_populates="books"
    )


class Author(Base):
    __tablename__ = "authors"
    name: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    bio: Mapped[str | None]
    date_of_birth: Mapped[str | None]


class HandingBookUser(Base):
    __tablename__ = "handing_books_users"
    __table_args__ = (UniqueConstraint("book_id", "user_id", name="uq_user_book"),)

    book_id: Mapped[int] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    amount: Mapped[int] = mapped_column(default=1, server_default="1")

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    book_return_date: Mapped[datetime | None]