from logging import getLogger

from pydantic import BaseModel
from sqlalchemy import update, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from ..models.base import User
from ..models.base_dao import BaseDAO


logger = getLogger(__name__)


class UsersDAO(BaseDAO):
    model: User = User

    @classmethod
    async def get_user_with_books(cls, user_id, session: AsyncSession) -> list[User]:
        query = (select(User).options(selectinload(User.books),).order_by(User.id)).filter_by(id=user_id)
        users = await session.scalars(query)
        return list(users)


    # @classmethod
    # async def update(cls, session: AsyncSession, user_id: int, values: BaseModel):
    #     # Обновить записи по фильтрам

    #     values_dict = values.model_dump(exclude_unset=True)
    #     logger.info(f"Обновлениы записи для {cls.model.__name__} по iD: {user_id} с параметрами: {values_dict}")
    #     query = (
    #         update(cls.model)
    #         .where(cls.model.id == user_id)
    #         .values(**values_dict)
    #     )
    #     try:
    #         await session.execute(query)
    #         await session.flush()
    #         logger.info(f"Обновлена информация для записи {cls.model.email}.")
    #     except SQLAlchemyError as e:
    #         await session.rollback()
    #         logger.error(f"Ошибка при обновлении записей: {e}")
            
