from logging import getLogger
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, Query, status


from ..models.db_helper import db_helper
from .schemes import HandingBookAddDB, BookUpdateDB, BooksInfo, HandingBookFind
from .crud import HandingBookUserDAO, BookDAO
from ..auth.dependencies import get_current_user, get_current_admin
from ..auth.crud import UsersDAO

router = APIRouter(prefix="/api_library", tags=["Library"])

logger = getLogger(__name__)


@router.post("/take_book/{book_id}/{amount}")
async def take_book(
    book_id: int,
    amount: int,
    user_data=Depends(get_current_user),
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    now = datetime.now()
    
    book_return_date = now + timedelta(days=7)
    book = await BookDAO.find_one_or_none_by_id(values=int(book_id), session=session)
    users_book_info = await UsersDAO.get_user_with_books(user_id=user_data.id, session=session)

    if len(users_book_info[0].books) == 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Вы не можете взять больше 5 книг",
        )
        
    if book.amount < amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недостаточно книг на складе",
        )
    chang_amount = book.amount - amount
    await BookDAO.update(
        session=session, base=book, values=BookUpdateDB(amount=chang_amount)
    )

    await HandingBookUserDAO.add(
        session=session,
        values=HandingBookAddDB(
            book_id=book_id,
            user_id=user_data.id,
            amount=amount,
            book_return_date=book_return_date,
        ),
    )
    await session.commit()
    return {"message": f"{user_data.first_name} взял {amount} книги {book.title}"}

@router.patch("/return_books/{book_id}")
async def return_books(
    book_id: int,
    user_data = Depends(get_current_user),
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    info_about_book = await HandingBookUserDAO.find_one_or_none(session=session, filters=HandingBookFind(book_id=book_id, user_id=user_data.id))
    if not info_about_book:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Вы не взяли эту книгу",
        )
    if info_about_book.book_return_date < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Вы не успели вернуть книгу вовремя, теперь вы должны её выкупить",
        )
    book = await BookDAO.find_one_or_none_by_id(values=int(book_id), session=session)
    chang_amount = book.amount + info_about_book.amount
    await BookDAO.update(
        session=session, base=book, values=BookUpdateDB(amount=chang_amount)
    )

    await session.delete(info_about_book)
    await session.commit()
    return {"message": f"{user_data.first_name} вернул {info_about_book.amount}"}
    

@router.get("/get_books_users/{book_id}", response_model=BooksInfo)
async def get_user_books(
    book_id: int,
    admin = Depends(get_current_admin),
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> BooksInfo:
    result = await BookDAO.get_books_with_users(book_id=book_id, session=session)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Такой книги нет",
        )
    return result[0]

@router.get("/books/")
async def get_book_info(
        author_id: int | None = None,
        page: int = Query(1, ge=1, description="Номер страницы"),
        page_size: int = Query(10, ge=10, le=50, description="Записей на странице"),
        session: AsyncSession = Depends(db_helper.session_dependency),
) -> dict:
    result = await BookDAO.get_book_list(session=session, author_id=author_id, page=page,
                                             page_size=page_size)
    return result