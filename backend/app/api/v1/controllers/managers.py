from fastapi import HTTPException
from sqlmodel import select
from typing import Annotated
from fastapi import Depends

from app.api.v1.models.user import ManagerCreateRequest, ManagerCreateResponse
from app.database import DBSessionDep
from app.services.security import get_password_hash
from app.sqlmodels.user import User, Role


class UserController:
    def __init__(self, db_session: DBSessionDep):
        self.db_session = db_session

    async def create_manager(self, data: ManagerCreateRequest, user: User) -> User:
        existing = await self.db_session.execute(
            select(User).where(User.email == data.email)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already registered")

        new_user = User(
            email=data.email,
            hashed_password=get_password_hash(data.password),
            nickname=data.nickname,
            role=Role.MANAGER,
            is_active=True,
        )

        self.db_session.add(new_user)
        await self.db_session.commit()
        await self.db_session.refresh(new_user)
        return new_user

    async def get_all_managers(self) -> list[User]:
        result = await self.db_session.execute(
            select(User).where(
                (User.role == Role.MANAGER) &
                (User.is_active == True)
            )
        )
        return list(result.scalars().all())

    async def deactivate_manager(self, manager_id: int, admin_user: User) -> None:
        if admin_user.role != Role.ADMIN:
            raise HTTPException(status_code=403, detail="Only admins can deactivate managers")

        result = await self.db_session.execute(
            select(User).where(User.id == manager_id)
        )
        manager = result.scalar_one_or_none()

        if not manager:
            raise HTTPException(status_code=404, detail="Manager not found")

        if manager.role != Role.MANAGER:
            raise HTTPException(status_code=400, detail="Only managers can be deactivated through this endpoint")

        manager.is_active = False
        await self.db_session.commit()


# Фабрика контроллера
def get_user_controller(
    db_session: DBSessionDep,
) -> UserController:
    return UserController(db_session=db_session)

# Зависимость
UserControllerDep = Annotated[UserController, Depends(get_user_controller)]