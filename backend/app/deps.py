from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from jose.exceptions import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api.v1.models.user import UserResponse
from app.database import get_session
from app.sqlmodels.user import User, Role
from app.settings import settings # ← импортируем Pydantic-схему

bearer_scheme = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db_session: AsyncSession = Depends(get_session)
) -> UserResponse:  # ← возвращаем Pydantic, не ORM!
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db_session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Важно: конвертируем ORM → Pydantic
    return UserResponse.model_validate(user)


async def get_current_admin(
    user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    if user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can perform this action"
        )
    return user


# Определяем зависимости как "готовые к использованию"
AuthUserDep = Annotated[UserResponse, Depends(get_current_user)]
AdminUserDep = Annotated[UserResponse, Depends(get_current_admin)]