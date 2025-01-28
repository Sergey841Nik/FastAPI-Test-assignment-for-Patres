from logging import getLogger

from pydantic import BaseModel

from sqlalchemy import select, update, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from .base import Base

logger = getLogger(__name__)


class BaseDAO:
    model: Base

    @classmethod
    async def find_one_or_none_by_id(cls, user_id: int, session: AsyncSession):
        # Найти запись по ID
        logger.info(f"Поиск {cls.model.__name__} с ID: {user_id}")
        try:
            query = select(cls.model).filter_by(id=user_id)
            result = await session.execute(query)
            user = result.scalar_one_or_none()
            if user:
                logger.info(f"Запись с ID {user_id} найдена.")
            else:
                logger.info(f"Запись с ID {user_id} не найдена.")
            return user
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске записи с ID {user_id}: {e}")
            raise

    @classmethod
    async def find_one_or_none(cls, session: AsyncSession, filters: BaseModel):
        # найти одно
        filter_dict = filters.model_dump(exclude_unset=True)

        logger.info("Поиск одной записи по фильтрам: %s" % filter_dict)

        query = select(cls.model).filter_by(**filter_dict)
        result = await session.execute(query)

        user = result.scalar_one_or_none()

        if user:
            logger.info("Запись найдена по фильтрам: %s" % filter_dict)
        else:
            logger.info("Запись не найдена по фильтрам: %s" % filter_dict)
        return user

    @classmethod
    async def add(cls, session: AsyncSession, values: BaseModel):
        # Добавить одну запись
        values_dict = values.model_dump(exclude_unset=True)

        logger.info("Добавление записи с параметрами: %s" % values_dict["password"])

        new_user = cls.model(**values_dict)
        session.add(new_user)

        await session.commit()
        logger.info(f"Запись успешно добавлена.")
        return new_user

    @classmethod
    async def get_all(cls, session: AsyncSession, filters: BaseModel | None):
        # найти всё
        if filters:
            filter_dict = filters.model_dump(exclude_unset=True)
        else:
            filter_dict = {}

        logger.info("Поиск одной записи по фильтрам: %s" % filter_dict)

        query = select(cls.model).filter_by(**filter_dict)
        result = await session.execute(query)
        users = result.scalars().all()
        if users:
            logger.info("Запись найдена по фильтрам: %s" % filter_dict)
        else:
            logger.info("Запись не найдена по фильтрам: %s" % filter_dict)
        return users
