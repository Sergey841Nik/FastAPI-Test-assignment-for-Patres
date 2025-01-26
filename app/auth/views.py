from logging import getLogger
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, Response, status, Form


from ..models.db_helper import db_helper
from .schemes import EmailModel, UserRegister, UserAddDB
from .crud import find_one_or_none_users, add_users

router = APIRouter(prefix='/auth', tags=['Auth'])

logger = getLogger(__name__)

@router.post("/register/", status_code=status.HTTP_201_CREATED)
async def register_users(
    user: UserRegister, 
    session: AsyncSession = Depends(db_helper.session_dependency)
) -> dict:
    find_user = await find_one_or_none_users(session=session, filters=EmailModel(email=user.email))
    if find_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail='Пользователь уже существует')
    
    user_dict = user.model_dump()
    
    del user_dict['confirm_password']
    await add_users(session=session, values=UserAddDB(**user_dict))
    return {'message': f'Вы успешно зарегистрированы!'}