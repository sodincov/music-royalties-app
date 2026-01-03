# app/api/v1/controllers/album.py
from fastapi import HTTPException, status
from sqlalchemy import delete
from sqlmodel import select
from typing import List
from app.database import DBSessionDep
from app.api.v1.models.album import AlbumCreateRequest, AlbumResponse, AlbumDetailResponse, AlbumUpdateRequest
from app.api.v1.models.artist import ArtistResponse
from app.sqlmodels.album import Album
from app.sqlmodels.artist import Artist
from app.sqlmodels.album_artist import AlbumArtist
from app.sqlmodels.user import User, Role

class AlbumController:
    def __init__(self, db_session: DBSessionDep):
        self.db_session = db_session

    def _ensure_admin(self, current_user: User) -> None:
        if current_user.role != Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: admin only"
            )

    async def _get_album_by_id(self, album_id: int) -> Album:
        result = await self.db_session.execute(
            select(Album).where(Album.id == album_id)
        )
        album = result.scalar_one_or_none()
        if not album:
            raise HTTPException(status_code=404, detail="Album not found")
        return album

    # === Все методы теперь принимают current_user как параметр ===

    async def create_album(
        self,
        data:AlbumCreateRequest,
        current_user: User
    ) -> AlbumResponse:
        # ... (вся логика как раньше, но используй current_user вместо self.current_user)
        if data.artist_ids:
            artist_result = await self.db_session.execute(
                select(Artist).where(Artist.id.in_(data.artist_ids))
            )
            found_artists = artist_result.scalars().all()
            if len(found_artists) != len(data.artist_ids):
                raise HTTPException(status_code=400, detail="One or more artists not found")

        if data.upc:
            existing_upc = await self.db_session.execute(
                select(Album).where(Album.upc == data.upc, Album.is_approved == True)
            )
            if existing_upc.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="UPC already exists")

        if data.isrc:
            existing_isrc = await self.db_session.execute(
                select(Album).where(Album.isrc == data.isrc, Album.is_approved == True)
            )
            if existing_isrc.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="ISRC already exists")

        is_approved = (current_user.role == Role.ADMIN)

        new_album = Album(
            title=data.title,
            type=data.type,
            release_date=data.release_date,
            upc=data.upc,
            marketing_expenses=data.marketing_budget,
            advance_expenses=data.advance,
            aggregator=data.aggregator,
            yoga=data.yoga,
            additional_sites=data.additional_sites,
            version=data.version,
            subgenre=data.subgenre,
            isrc=data.isrc,
            zaycev_star=data.zaycev_star,
            synclab_star=data.synclab_star,
            is_approved=is_approved,
            created_by_user_id=current_user.id,
        )

        self.db_session.add(new_album)
        await self.db_session.flush()

        for artist_id in data.artist_ids:
            link = AlbumArtist(album_id=new_album.id, artist_id=artist_id)
            self.db_session.add(link)

        await self.db_session.commit()
        await self.db_session.refresh(new_album)

        if not is_approved:
            raise HTTPException(
                status_code=status.HTTP_202_ACCEPTED,
                detail="Album created as draft. Awaiting admin approval."
            )

        return AlbumResponse(
            id=new_album.id,
            title=new_album.title,
            type=new_album.type,
            release_date=new_album.release_date,
            upc=new_album.upc,
            marketing_budget=new_album.marketing_expenses,
            advance=new_album.advance_expenses,
            aggregator=new_album.aggregator,
            yoga=new_album.yoga,
            additional_sites=new_album.additional_sites,
            version=new_album.version,
            subgenre=new_album.subgenre,
            isrc=new_album.isrc,
            zaycev_star=new_album.zaycev_star,
            synclab_star=new_album.synclab_star,
            is_approved=new_album.is_approved,
        )

    async def get_all_albums(self) -> List[AlbumDetailResponse]:
        result = await self.db_session.execute(
            select(Album).where(Album.is_approved == True)
        )
        albums = result.scalars().all()
        return await self._build_album_detail_list(albums)

    async def get_album_drafts(self, current_user: User) -> List[AlbumDetailResponse]:
        self._ensure_admin(current_user)
        result = await self.db_session.execute(
            select(Album).where(Album.is_approved == False)
        )
        drafts = result.scalars().all()
        return await self._build_album_detail_list(drafts)

    async def _build_album_detail_list(self, albums) -> List[AlbumDetailResponse]:
        responses = []
        for album in albums:
            album_artist_result = await self.db_session.execute(
                select(AlbumArtist).where(AlbumArtist.album_id == album.id)
            )
            artist_ids = [aa.artist_id for aa in album_artist_result.scalars().all()]
            artists = []
            if artist_ids:
                artists_result = await self.db_session.execute(
                    select(Artist).where(Artist.id.in_(artist_ids))
                )
                artists_data = artists_result.scalars().all()
                artists = [
                    ArtistResponse(
                        id=a.id,
                        name=a.name,
                        isni=a.isni,
                        is_approved=a.is_approved,  # ← добавили!
                        created_by_user_id=a.created_by_user_id,
                    )
                    for a in artists_data
                ]
            responses.append(
                AlbumDetailResponse(
                    id=album.id,
                    title=album.title,
                    type=album.type,
                    release_date=album.release_date,
                    upc=album.upc,
                    artists=artists,
                    tracks=[],
                    version=album.version,
                    subgenre=album.subgenre,
                    isrc=album.isrc,
                    is_approved=album.is_approved,
                )
            )
        return responses

    async def approve_album_draft(self, album_id: int, current_user: User) -> AlbumResponse:
        self._ensure_admin(current_user)
        album = await self._get_album_by_id(album_id)
        if album.is_approved:
            raise HTTPException(status_code=400, detail="Album is already approved")

        album.is_approved = True
        self.db_session.add(album)
        await self.db_session.commit()
        await self.db_session.refresh(album)

        return AlbumResponse(
            id=album.id,
            title=album.title,
            type=album.type,
            release_date=album.release_date,
            upc=album.upc,
            marketing_budget=album.marketing_expenses,
            advance=album.advance_expenses,
            aggregator=album.aggregator,
            yoga=album.yoga,
            additional_sites=album.additional_sites,
            version=album.version,
            subgenre=album.subgenre,
            isrc=album.isrc,
            zaycev_star=album.zaycev_star,
            synclab_star=album.synclab_star,
            is_approved=album.is_approved,
        )

    async def reject_album_draft(self, album_id: int, current_user: User) -> None:
        self._ensure_admin(current_user)
        album = await self._get_album_by_id(album_id)
        if album.is_approved:
            raise HTTPException(status_code=400, detail="Cannot reject already approved album")

        await self.db_session.execute(
            delete(AlbumArtist).where(AlbumArtist.album_id == album_id)
        )
        await self.db_session.delete(album)
        await self.db_session.commit()

    async def get_album_by_id(self, album_id: int, current_user: User) -> AlbumDetailResponse:
        album = await self._get_album_by_id(album_id)

        if album.is_approved:
            albums = [album]
        elif album.created_by_user_id == current_user.id or current_user.role == Role.ADMIN:
            albums = [album]
        else:
            raise HTTPException(status_code=404, detail="Album not found")

        detail_list = await self._build_album_detail_list(albums)
        return detail_list[0]

    async def update_album(
        self,
        album_id: int,
        data: AlbumUpdateRequest,
        current_user: User
    ) -> AlbumResponse:
        album = await self._get_album_by_id(album_id)

        if album.is_approved and current_user.role != Role.ADMIN:
            raise HTTPException(status_code=403, detail="Only admin can edit approved albums")
        if not album.is_approved and album.created_by_user_id != current_user.id:
            raise HTTPException(status_code=403, detail="You can only edit your own drafts")

        if data.upc is not None and data.upc != album.upc:
            exists = await self.db_session.execute(
                select(Album).where(Album.upc == data.upc, Album.is_approved == True)
            )
            if exists.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="UPC already exists")

        if data.isrc is not None and data.isrc != album.isrc:
            exists = await self.db_session.execute(
                select(Album).where(Album.isrc == data.isrc, Album.is_approved == True)
            )
            if exists.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="ISRC already exists")

        update_data = data.model_dump(exclude_unset=True, exclude={'artist_ids'})
        for key, value in update_data.items():
            if key == 'marketing_budget':
                setattr(album, 'marketing_expenses', float(value) if value is not None else None)
            elif key == 'advance':
                setattr(album, 'advance_expenses', float(value) if value is not None else None)
            else:
                setattr(album, key, value)

        if data.artist_ids is not None:
            await self.db_session.execute(
                delete(AlbumArtist).where(AlbumArtist.album_id == album_id)
            )
            if data.artist_ids:
                artist_result = await self.db_session.execute(
                    select(Artist).where(Artist.id.in_(data.artist_ids))
                )
                found = artist_result.scalars().all()
                if len(found) != len(data.artist_ids):
                    raise HTTPException(status_code=400, detail="Some artist IDs do not exist")
                for aid in data.artist_ids:
                    self.db_session.add(AlbumArtist(album_id=album.id, artist_id=aid))

        self.db_session.add(album)
        await self.db_session.commit()
        await self.db_session.refresh(album)

        return AlbumResponse(
            id=album.id,
            title=album.title,
            type=album.type,
            release_date=album.release_date,
            upc=album.upc,
            marketing_budget=album.marketing_expenses,
            advance=album.advance_expenses,
            aggregator=album.aggregator,
            yoga=album.yoga,
            additional_sites=album.additional_sites,
            version=album.version,
            subgenre=album.subgenre,
            isrc=album.isrc,
            zaycev_star=album.zaycev_star,
            synclab_star=album.synclab_star,
            is_approved=album.is_approved,
        )

    async def delete_album(self, album_id: int, current_user: User) -> bool:
        self._ensure_admin(current_user)
        album = await self._get_album_by_id(album_id)
        await self.db_session.execute(
            delete(AlbumArtist).where(AlbumArtist.album_id == album_id)
        )
        await self.db_session.delete(album)
        await self.db_session.commit()
        return True

# ✅ ФИНАЛЬНАЯ СТРОКА: только DBSessionDep
from typing import Annotated
from fastapi import Depends

AlbumControllerDep = Annotated[AlbumController, Depends(AlbumController)]