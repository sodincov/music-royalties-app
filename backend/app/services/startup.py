# app/core/startup.py
from typing import Optional
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.services.security import get_password_hash
from app.sqlmodels.user import User, Role



async def create_first_admin(
    email: str = "admin@localhost",
    password: str = "admin",
    nickname: Optional[str] = "SuperAdmin"
) -> None:
    async with AsyncSessionLocal() as session:  # ← Так правильно!
        try:
            # Проверяем, есть ли уже админ
            stmt = select(User).where(User.role == Role.ADMIN)
            result = await session.execute(stmt)
            existing_admin = result.scalars().first()

            if existing_admin:
                print("✅ Admin already exists. Skipping creation.")
                return

            # Создаём админа
            admin = User(
                email=email,
                hashed_password=get_password_hash(password),
                nickname=nickname,
                role=Role.ADMIN,
                is_active=True,
            )

            session.add(admin)
            await session.commit()
            await session.refresh(admin)
            print(f"🎉 First admin created! Email: {admin.email}, Role: {admin.role}")

        except IntegrityError:
            await session.rollback()
            print("❌ Admin creation failed: email already exists or database constraint violation.")
        except Exception as e:
            await session.rollback()
            print(f"❌ Unexpected error during admin creation: {e}")