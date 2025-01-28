from logging import getLogger

from pydantic import BaseModel
from sqlalchemy import select, update, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from ..models.base import User
from ..models.base_dao import BaseDAO


logger = getLogger(__name__)


class UsersDAO(BaseDAO):
    model = User
