from logging import getLogger

from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.base import Book, Author, HandingBookUser
from ..models.base_dao import BaseDAO


logger = getLogger(__name__)


class BookDAO(BaseDAO):
    model: Book = Book

    @classmethod
    async def get_books_with_users(cls, book_id, session: AsyncSession) -> list[Book]:
        query = (select(Book).options(selectinload(Book.users),).filter_by(id=book_id))
        books = await session.scalars(query)
        logger.info("Найдены %s." % books)
        return list(books)

class AuthorDAO(BaseDAO):
    model: Author = Author

class HandingBookUserDAO(BaseDAO):
    model: HandingBookUser = HandingBookUser
