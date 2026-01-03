# app/api/v1/controllers/artist.py
from fastapi import HTTPException, status
from sqlalchemy import delete
from sqlalchemy.orm import selectinload
from sqlmodel import select
from typing import List

from app.api.v1.models.user import UserResponse
from app.database import DBSessionDep
from app.api.v1.models.artist import ArtistCreateRequest, ArtistResponse, ArtistDetailResponse, ArtistUpdateRequest
from app.api.v1.models.person import PersonResponse
from app.sqlmodels.artist import Artist
from app.sqlmodels.person import Person
from app.sqlmodels.artist_person import ArtistPerson
from app.sqlmodels.user import User, Role

from fastapi import HTTPException, status
from sqlalchemy import delete
from sqlalchemy.orm import selectinload
from sqlmodel import select
from typing import List, Optional
from app.database import DBSessionDep
from app.api.v1.models.artist import (
    ArtistCreateRequest,
    ArtistResponse,
    ArtistDetailResponse,
    ArtistUpdateRequest
)
from app.api.v1.models.person import PersonResponse
from app.sqlmodels.artist import Artist
from app.sqlmodels.person import Person
from app.sqlmodels.artist_person import ArtistPerson

from app.sqlmodels.user import Role


class ArtistController:
    def __init__(self, db_session: DBSessionDep):
        self.db_session = db_session

    def _ensure_admin(self, current_user: UserResponse) -> None:
        if current_user.role != Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: admin only"
            )

    async def _get_artist_by_id(self, artist_id: int, load_members: bool = True) -> Artist:
        query = select(Artist).where(Artist.id == artist_id)
        if load_members:
            query = query.options(selectinload(Artist.members))
        result = await self.db_session.execute(query)
        artist = result.scalar_one_or_none()
        if not artist:
            raise HTTPException(status_code=404, detail="Artist not found")
        return artist

    async def create_artist(
        self,
        data:ArtistCreateRequest,
        current_user: UserResponse
    ) -> ArtistResponse:
        if data.isni:
            existing_isni = await self.db_session.execute(
                select(Artist).where(Artist.isni == data.isni, Artist.is_approved == True)
            )
            if existing_isni.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="ISNI already exists")

        if data.member_ids:
            persons_result = await self.db_session.execute(
                select(Person).where(Person.id.in_(data.member_ids))
            )
            found_persons = persons_result.scalars().all()
            if len(found_persons) != len(data.member_ids):
                raise HTTPException(status_code=400, detail="Some person IDs do not exist")

        is_approved = (current_user.role == Role.ADMIN)

        new_artist = Artist(
            name=data.name,
            isni=data.isni,
            is_approved=is_approved,
            created_by_user_id=current_user.id,
        )

        self.db_session.add(new_artist)
        await self.db_session.commit()
        await self.db_session.refresh(new_artist)

        for person_id in data.member_ids:
            link = ArtistPerson(artist_id=new_artist.id, person_id=person_id)
            self.db_session.add(link)
        await self.db_session.commit()

        # ✅ Всегда возвращаем объект — НЕТ raise HTTPException(202)
        return ArtistResponse(
            id=new_artist.id,
            name=new_artist.name,
            isni=new_artist.isni,
            is_approved=new_artist.is_approved,  # ← добавь это в модель!
        )

    async def get_all_artists(self) -> List[ArtistDetailResponse]:
        result = await self.db_session.execute(
            select(Artist)
            .where(Artist.is_approved == True)
            .options(selectinload(Artist.members))
        )
        artists = result.scalars().all()
        return self._build_artist_detail_list(artists)

    async def get_artist_drafts(self, current_user: UserResponse) -> List[ArtistDetailResponse]:
        self._ensure_admin(current_user)
        result = await self.db_session.execute(
            select(Artist)
            .where(Artist.is_approved == False)
            .options(selectinload(Artist.members))
        )
        drafts = result.scalars().all()
        return self._build_artist_detail_list(drafts)

    def _build_artist_detail_list(self, artists) -> List[ArtistDetailResponse]:
        return [self._build_artist_detail(a) for a in artists]

    def _build_artist_detail(self, artist: Artist) -> ArtistDetailResponse:
        return ArtistDetailResponse(
            id=artist.id,
            name=artist.name,
            isni=artist.isni,
            members=[
                PersonResponse(
                    id=p.id,
                    last_name=p.last_name,
                    first_name=p.first_name,
                    middle_name=p.middle_name,
                    email=p.email,
                    phone=p.phone,
                    is_approved=p.is_approved,
                    created_by_user_id=p.created_by_user_id,
                )
                for p in artist.members
            ]
        )

    async def approve_artist_draft(self, artist_id: int, current_user: UserResponse) -> ArtistResponse:
        self._ensure_admin(current_user)
        artist = await self._get_artist_by_id(artist_id)
        if artist.is_approved:
            raise HTTPException(status_code=400, detail="Artist is already approved")

        artist.is_approved = True
        self.db_session.add(artist)
        await self.db_session.commit()
        await self.db_session.refresh(artist)

        return ArtistResponse(id=artist.id, name=artist.name, isni=artist.isni)

    async def reject_artist_draft(self, artist_id: int, current_user: UserResponse) -> None:
        self._ensure_admin(current_user)
        artist = await self._get_artist_by_id(artist_id)
        if artist.is_approved:
            raise HTTPException(status_code=400, detail="Cannot reject already approved artist")

        await self.db_session.execute(
            delete(ArtistPerson).where(ArtistPerson.artist_id == artist_id)
        )
        await self.db_session.delete(artist)
        await self.db_session.commit()

    async def get_artist_by_id(self, artist_id: int, current_user: UserResponse) -> ArtistDetailResponse:
        artist = await self._get_artist_by_id(artist_id)

        if artist.is_approved:
            return self._build_artist_detail(artist)
        if artist.created_by_user_id == current_user.id or current_user.role == Role.ADMIN:
            return self._build_artist_detail(artist)

        raise HTTPException(status_code=404, detail="Artist not found")

    async def update_artist(
        self,
        artist_id: int,
        data:ArtistUpdateRequest,
        current_user: UserResponse
    ) -> ArtistResponse:
        artist = await self._get_artist_by_id(artist_id)

        if artist.is_approved and current_user.role != Role.ADMIN:
            raise HTTPException(status_code=403, detail="Only admin can edit approved artists")
        if not artist.is_approved and artist.created_by_user_id != current_user.id:
            raise HTTPException(status_code=403, detail="You can only edit your own drafts")

        if data.isni is not None and data.isni != artist.isni:
            exists = await self.db_session.execute(
                select(Artist).where(Artist.isni == data.isni, Artist.is_approved == True)
            )
            if exists.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="ISNI already exists")

        update_data = data.model_dump(exclude_unset=True, exclude={"member_ids"})
        for key, value in update_data.items():
            setattr(artist, key, value)

        if data.member_ids is not None:
            await self.db_session.execute(
                delete(ArtistPerson).where(ArtistPerson.artist_id == artist_id)
            )
            if data.member_ids:
                persons = await self.db_session.execute(
                    select(Person).where(Person.id.in_(data.member_ids))
                )
                found = persons.scalars().all()
                if len(found) != len(data.member_ids):
                    raise HTTPException(status_code=400, detail="Some person IDs do not exist")
                for pid in data.member_ids:
                    self.db_session.add(ArtistPerson(artist_id=artist.id, person_id=pid))

        self.db_session.add(artist)
        await self.db_session.commit()
        await self.db_session.refresh(artist)

        return ArtistResponse(id=artist.id, name=artist.name, isni=artist.isni)

    async def delete_artist(self, artist_id: int, current_user: UserResponse) -> None:
        self._ensure_admin(current_user)
        artist = await self._get_artist_by_id(artist_id)
        await self.db_session.execute(
            delete(ArtistPerson).where(ArtistPerson.artist_id == artist_id)
        )
        await self.db_session.delete(artist)
        await self.db_session.commit()
        # Ничего не возвращаем

# ✅ ФИНАЛЬНАЯ СТРОКА: только DBSessionDep
from typing import Annotated
from fastapi import Depends

ArtistControllerDep = Annotated[ArtistController, Depends(ArtistController)]