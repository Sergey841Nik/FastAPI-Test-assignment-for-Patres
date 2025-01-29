from logging import getLogger
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, Response, status, Form


from ..models.db_helper import db_helper
from .schemes import EmailModel, UserRegister, UserAddDB, UserAuth, UserInfo

# from .crud import find_one_or_none_users, add_users, get_all_users
from .crud import UsersDAO
from .auth_jwt import validate_auth_user, create_access_token
from .dependencies import get_current_user, get_current_admin

router = APIRouter(prefix="/auth", tags=["Auth"])

logger = getLogger(__name__)


@router.post("/register/", status_code=status.HTTP_201_CREATED)
async def register_users(
    user: UserRegister, session: AsyncSession = Depends(db_helper.session_dependency)
) -> dict:
    find_user = await UsersDAO.find_one_or_none(
        session=session, filters=EmailModel(email=user.email)
    )
    if find_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Пользователь уже существует"
        )

    user_dict = user.model_dump()

    del user_dict["confirm_password"]
    await UsersDAO.add(session=session, values=UserAddDB(**user_dict))
    return {"message": f"Вы успешно зарегистрированы!"}


@router.post("/login/")
async def auth_user(
    response: Response,
    user: UserAuth,
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> dict:

    check_user = await validate_auth_user(
        email=user.email, password=user.password, session=session
    )

    access_token = create_access_token(check_user)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return {"ok": True, "access_token": access_token, "message": "Авторизация успешна!"}


@router.post("/logout/")
async def logout_user(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Пользователь успешно вышел из системы"}


@router.put("/change_info_user_self/")
async def change_role(
    user: UserRegister,
    session: AsyncSession = Depends(db_helper.session_dependency),
    user_data=Depends(get_current_user),
):
    user_dict = user.model_dump()
    del user_dict["confirm_password"]

    await UsersDAO.update(
        session=session, user=user_data, values=UserAddDB(**user_dict)
    )
    await session.commit()

    return {"message": "Данные пользователя изменены"}


@router.get("/me/")
async def get_me(user_data=Depends(get_current_user)) -> UserInfo:
    return UserInfo.model_validate(user_data)


@router.get("/all_users/")
async def all_users(
    session: AsyncSession = Depends(db_helper.session_dependency),
    user_data=Depends(get_current_admin),
) -> list[UserInfo]:
    return await UsersDAO.get_all(session=session, filters=None)  # type: ignore
