from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import HTTPException, status
from jose import jwt
from passlib.context import CryptContext

from sqlalchemy import select
from typing import Annotated

from fastapi import Depends

from app.services.auth import verify_password
from app.settings import settings
from app.database import DBSessionDep
from app.sqlmodels.user import User
from app.api.v1.models.auth import TokenResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthController:
    def __init__(self, db_session: DBSessionDep):
        self.db_session = db_session

    def _verify_password(self, plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain, hashed)

    async def _get_user_by_email(self, email: str) -> Optional[User]:
        result = await self.db_session.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def authenticate_and_create_token(self, email: str, password: str):
        result = await self.db_session.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=401,
                detail="Incorrect email or password"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=401,
                detail="Account is deactivated. Contact administrator."  # ← Сообщение
            )

        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=401,
                detail="Incorrect email or password"
            )

        expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        to_encode = {"sub": user.email, "role": user.role.value}
        expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
        to_encode.update({"exp": expire})

        token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

        return TokenResponse(access_token=token)

AuthControllerDep = Annotated[AuthController, Depends(AuthController)]