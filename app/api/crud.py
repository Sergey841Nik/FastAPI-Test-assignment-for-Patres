from logging import getLogger

from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

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
    
    @classmethod
    async def get_book_list(
        cls, 
        session: AsyncSession, 
        author_id: int | None = None,
        page: int = 1, 
        page_size: int = 10
    ):
        "Получает список книг с возможностью фильтрации и пагинации."
        # Ограничение параметров
        page_size = max(3, min(page_size, 50))
        page = max(1, page)

        # Начальная сборка базового запроса
        base_query = select(Book).options(
            joinedload(Book.authors),
        )

        # Фильтрация по автору
        if author_id is not None:
            base_query = base_query.filter_by(author=author_id)

        # Подсчет общего количества книг
        count_query = select(func.count()).select_from(base_query.subquery())
        total_result = await session.scalar(count_query)

        # Если книг нет, возвращаем пустой результат
        if not total_result:
            return {
                "page": page,
                "total_page": 0,
                "total_result": 0, 
            }
        
        # Расчет количества страниц
        total_page = (total_result + page_size - 1) // page_size

        # Применение пагинации
        offset = (page - 1) * page_size
        paginated_query = base_query.offset(offset).limit(page_size)

        # Выполнение запроса и получение результатов
        result = await session.execute(paginated_query)
        books = result.scalars().all()

        filters = []
        if author_id:
            filters.append(f"author_id={author_id}")
        
        filter_str = " & ".join(filters) if filters else "no filters"

        logger.info("Страница %s c %d книг, фильтр: %s." % (page, len(books), filter_str))

        # Формирование результата
        return {
            "page": page,
            "total_page": total_page,
            "total_result": total_result,
            "blogs": books
        }



class AuthorDAO(BaseDAO):
    model: Author = Author

class HandingBookUserDAO(BaseDAO):
    model: HandingBookUser = HandingBookUser
