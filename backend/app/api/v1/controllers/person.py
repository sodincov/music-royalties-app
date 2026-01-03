from fastapi import HTTPException, status, Depends
from sqlmodel import select
from typing import List, Optional, Annotated

from app.api.v1.models.user import UserResponse
from app.database import DBSessionDep
from app.sqlmodels.person import Person
from app.sqlmodels.user import User, Role
from app.api.v1.models.person import PersonCreateRequest, PersonResponse, PersonUpdateRequest

class PersonController:
    def __init__(self, db_session: DBSessionDep):
        self.db_session = db_session

    def _ensure_admin(self, current_user: User) -> None:
        if current_user.role != Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: admin only"
            )

    async def _get_person_by_id(self, person_id: int) -> Person:
        result = await self.db_session.execute(
            select(Person).where(Person.id == person_id)
        )
        person = result.scalar_one_or_none()
        if not person:
            raise HTTPException(status_code=404, detail="Person not found")
        return person

    # В контроллере
    async def create_person(
            self,
            data: PersonCreateRequest,
            current_user: User  # или UserRead — но убедись, что совпадает с роутером
    ) -> PersonResponse:
        # Проверяем email ТОЛЬКО среди УТВЕРЖДЁННЫХ персон
        existing_email = await self.db_session.execute(
            select(Person).where(Person.email == data.email, Person.is_approved == True)
        )
        if existing_email.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already exists")

        is_approved = (current_user.role == Role.ADMIN)

        new_person = Person(
            last_name=data.last_name,
            first_name=data.first_name,
            middle_name=data.middle_name,
            email=data.email,
            phone=data.phone,
            is_approved=is_approved,
            created_by_user_id=current_user.id,
        )

        self.db_session.add(new_person)
        await self.db_session.commit()
        await self.db_session.refresh(new_person)

        # Просто возвращаем объект — НИКАКИХ raise для 202!
        return PersonResponse(
            id=new_person.id,
            last_name=new_person.last_name,
            first_name=new_person.first_name,
            middle_name=new_person.middle_name,
            email=new_person.email,
            phone=new_person.phone,
            is_approved=new_person.is_approved,
            created_by_user_id=new_person.created_by_user_id,
        )

    async def get_all_people(self) -> List[PersonResponse]:
        result = await self.db_session.execute(
            select(Person).where(Person.is_approved == True)
        )
        people = result.scalars().all()
        return [
            PersonResponse.model_validate(p) for p in people
        ]

    async def get_person_drafts(self, current_user: User) -> List[PersonResponse]:
        self._ensure_admin(current_user)
        result = await self.db_session.execute(
            select(Person).where(Person.is_approved == False)
        )
        drafts = result.scalars().all()
        return [PersonResponse.model_validate(p) for p in drafts]

    async def approve_person_draft(self, person_id: int, current_user: User) -> PersonResponse:
        self._ensure_admin(current_user)
        person = await self._get_person_by_id(person_id)
        if person.is_approved:
            raise HTTPException(status_code=400, detail="Person is already approved")

        person.is_approved = True
        self.db_session.add(person)
        await self.db_session.commit()
        await self.db_session.refresh(person)
        return PersonResponse.model_validate(person)

    async def reject_person_draft(self, person_id: int, current_user: User) -> None:
        self._ensure_admin(current_user)
        person = await self._get_person_by_id(person_id)
        if person.is_approved:
            raise HTTPException(status_code=400, detail="Cannot reject already approved person")
        await self.db_session.delete(person)
        await self.db_session.commit()

    async def update_person(
        self,
        person_id: int,
        data: PersonUpdateRequest,
        current_user: User
    ) -> PersonResponse:
        person = await self._get_person_by_id(person_id)

        if person.is_approved and current_user.role != Role.ADMIN:
            raise HTTPException(status_code=403, detail="Only admin can edit approved persons")
        if not person.is_approved and person.created_by_user_id != current_user.id:
            raise HTTPException(status_code=403, detail="You can only edit your own drafts")

        if data.email is not None and data.email != person.email:
            existing_email = await self.db_session.execute(
                select(Person).where(Person.email == data.email, Person.is_approved == True)
            )
            if existing_email.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="Email already exists")

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(person, key, value)

        self.db_session.add(person)
        await self.db_session.commit()
        await self.db_session.refresh(person)
        return PersonResponse.model_validate(person)

    async def get_person_by_id(self, person_id: int, current_user: User) -> PersonResponse:
        person = await self._get_person_by_id(person_id)

        if person.is_approved:
            return PersonResponse.model_validate(person)
        if person.created_by_user_id == current_user.id or current_user.role == Role.ADMIN:
            return PersonResponse.model_validate(person)
        raise HTTPException(status_code=404, detail="Person not found")

    async def delete_person(self, person_id: int, current_user: UserResponse) -> None:
        self._ensure_admin(current_user)
        person = await self._get_person_by_id(person_id)
        await self.db_session.delete(person)
        await self.db_session.commit()


# Зависимость теперь проще: только сессия БД
PersonControllerDep = Annotated[PersonController, Depends(PersonController)]