from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .crud import BookDAO
from .schemes import BookUpdateDB
from ..auth.crud import UsersDAO


async def chang_book(
        session: AsyncSession, 
        book_id: int, 
        user_id: int, 
        amount: int,
        flag = True
):
    now = datetime.now()
    book_return_date = now + timedelta(days=7)
    book = await BookDAO.find_one_or_none_by_id(values=int(book_id), session=session)
    users_book_info = await UsersDAO.get_user_with_books(user_id=user_id, session=session)

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
    if flag:
        chang_amount = book.amount - amount
    else:
        chang_amount = book.amount + amount
        
    await BookDAO.update(
        session=session, base=book, values=BookUpdateDB(amount=chang_amount)
    )

    return book_return_date