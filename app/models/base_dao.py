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
    async def find_one_or_none_by_id(cls, values: int, session: AsyncSession):
        # Найти запись по ID
        logger.info(f"Поиск {cls.model.__name__} с ID: {values}")
        try:
            query = select(cls.model).filter_by(id=values)
            result = await session.execute(query)
            value = result.scalar_one_or_none()
            if value:
                logger.info(f"Запись с ID {values} найдена.")
            else:
                logger.info(f"Запись с ID {values} не найдена.")
            return value
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске записи с ID {values}: {e}")
            raise

    @classmethod
    async def find_one_or_none(cls, session: AsyncSession, filters: BaseModel):
        # найти одно
        filter_dict = filters.model_dump(exclude_unset=True)

        logger.info("Поиск одной записи по фильтрам: %s" % filter_dict)

        query = select(cls.model).filter_by(**filter_dict)
        result = await session.execute(query)

        value = result.scalar_one_or_none()

        if value:
            logger.info("Запись найдена по фильтрам: %s" % filter_dict)
        else:
            logger.info("Запись не найдена по фильтрам: %s" % filter_dict)
        return value

    @classmethod
    async def add(cls, session: AsyncSession, values: BaseModel):
        # Добавить одну запись
        values_dict = values.model_dump(exclude_unset=True)

        logger.info("Добавление записи с параметрами: %s" % values_dict)

        new_value = cls.model(**values_dict)
        session.add(new_value)
        try:
            await session.flush()
            logger.info("Запись успешно добавлена.")
            return new_value
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при добавлении записей: {e}")
            await session.rollback()

    @classmethod
    async def get_all(cls, session: AsyncSession):
        # найти всё

        query = select(cls.model)
        result = await session.execute(query)
        value = result.scalars().all()
        if value:
            logger.info("Запись найдена")
        else:
            logger.info("Запись не найдена")
        return value

    @classmethod
    async def update(cls, session: AsyncSession, base: Base, values: BaseModel):
        # Обновить записи по фильтрам
        for key, value in values.model_dump(exclude_unset=True).items():
            setattr(base, key, value)

        try:
            await session.flush()
            logger.info("Обновлена информация для %s." % cls.model)
        except SQLAlchemyError as e:
            logger.error("Ошибка при обновлении записей: %s" % e)
            await session.rollback()