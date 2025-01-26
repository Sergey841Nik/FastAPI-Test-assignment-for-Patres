from datetime import datetime

from sqlalchemy import ForeignKey, Text, text, TIMESTAMP, func, String, UniqueConstraint
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


    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"


class Role(Base):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    users: Mapped[list["User"]] = relationship(back_populates="role")

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"