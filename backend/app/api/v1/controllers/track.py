# app/api/v1/controllers/track.py
from fastapi import HTTPException, status
from sqlalchemy import delete
from sqlmodel import select
from typing import List
from app.database import DBSessionDep
from app.api.v1.models.track import TrackResponse, TrackDetailResponse, TrackCreateRequest, TrackUpdateRequest, TrackPersonShareResponse
from app.api.v1.models.artist import ArtistResponse, ArtistDetailResponse
from app.api.v1.models.album import AlbumResponse
from app.sqlmodels import TrackPersonShare, Person
from app.sqlmodels.track import Track
from app.sqlmodels.album import Album
from app.sqlmodels.artist import Artist
from app.sqlmodels.track_artist import TrackArtist
from app.sqlmodels.user import User, Role

class TrackController:
    def __init__(self, db_session: DBSessionDep):
        self.db_session = db_session

    def _ensure_admin(self, current_user: User) -> None:
        if current_user.role != Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: admin only"
            )

    async def _get_track_by_id(self, track_id: int) -> Track:
        result = await self.db_session.execute(
            select(Track).where(Track.id == track_id)
        )
        track = result.scalar_one_or_none()
        if not track:
            raise HTTPException(status_code=404, detail="Track not found")
        return track

    async def create_track(
        self,
        data:TrackCreateRequest,
        current_user: User
    ) -> TrackResponse:
        # Проверка альбома
        album = await self.db_session.get(Album, data.album_id)
        if not album:
            raise HTTPException(status_code=404, detail="Album not found")

        if data.isrc:
            existing = await self.db_session.execute(
                select(Track).where(Track.isrc == data.isrc, Track.is_approved == True)
            )
            if existing.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="Track with this ISRC already exists")

        artist_result = await self.db_session.execute(
            select(Artist).where(Artist.id.in_(data.artist_ids))
        )
        found_artists = artist_result.scalars().all()
        if len(found_artists) != len(data.artist_ids):
            raise HTTPException(status_code=404, detail="One or more artists not found")

        is_approved = (current_user.role == Role.ADMIN)

        new_track = Track(
            title=data.title,
            album_id=data.album_id,
            isrc=data.isrc,
            genre=data.genre,
            music_authors=data.music_authors,
            lyrics_authors=data.lyrics_authors,
            scope_of_copyright=data.scope_of_copyright,
            scope_of_related_rights=data.scope_of_related_rights,
            neighboring_rights_share=data.neighboring_rights_share,
            label_rights_share=data.label_rights_share,
            label_monetization_share=data.label_monetization_share,
            artist_monetization_shares=data.artist_monetization_shares,
            marketing_expenses=data.marketing_expenses,
            advance_expenses=data.advance_expenses,
            advance=data.advance,
            marketing=data.marketing,
            text=data.text,
            karaoke=data.karaoke,
            synclab=data.synclab,
            copyright=data.copyright,
            related_rights=data.related_rights,
            is_ringtone_added=data.is_ringtone_added,
            has_video_clip=data.has_video_clip,
            is_lyrics_added=data.is_lyrics_added,
            is_karaoke_sync_added=data.is_karaoke_sync_added,
            is_approved=is_approved,
            created_by_user_id=current_user.id,
        )

        self.db_session.add(new_track)
        await self.db_session.flush()

        for artist_id in data.artist_ids:
            self.db_session.add(TrackArtist(track_id=new_track.id, artist_id=artist_id))

        if data.author_rights:
            for share_data in data.author_rights:
                person = await self.db_session.get(Person, share_data.person_id)
                if not person:
                    raise HTTPException(status_code=404, detail=f"Person with id {share_data.person_id} not found")
                existing = await self.db_session.execute(
                    select(TrackPersonShare).where(
                        TrackPersonShare.track_id == new_track.id,
                        TrackPersonShare.person_id == share_data.person_id
                    )
                )
                if not existing.scalar_one_or_none():
                    self.db_session.add(TrackPersonShare(
                        track_id=new_track.id,
                        person_id=share_data.person_id,
                        share_of_monetization_of_copyrights=float(share_data.share),
                        copyrights=float(share_data.licensor_share),
                        share_of_monetization_of_related_rights=0.0,
                        related_rights=0.0
                    ))

        if data.neighboring_rights:
            for share_data in data.neighboring_rights:
                person = await self.db_session.get(Person, share_data.person_id)
                if not person:
                    raise HTTPException(status_code=404, detail=f"Person with id {share_data.person_id} not found")
                existing = await self.db_session.execute(
                    select(TrackPersonShare).where(
                        TrackPersonShare.track_id == new_track.id,
                        TrackPersonShare.person_id == share_data.person_id
                    )
                )
                if not existing.scalar_one_or_none():
                    self.db_session.add(TrackPersonShare(
                        track_id=new_track.id,
                        person_id=share_data.person_id,
                        share_of_monetization_of_related_rights=float(share_data.share),
                        related_rights=float(share_data.licensor_share),
                        share_of_monetization_of_copyrights=0.0,
                        copyrights=0.0
                    ))

        await self.db_session.commit()
        await self.db_session.refresh(new_track, ["album", "artists"])

        if not is_approved:
            raise HTTPException(
                status_code=status.HTTP_202_ACCEPTED,
                detail="Track created as draft. Awaiting admin approval."
            )

        artists_resp = [
            ArtistResponse(
                id=a.id,
                name=a.name,
                isni=a.isni,
                is_approved=a.is_approved,
                created_by_user_id=a.created_by_user_id,
            )
            for a in new_track.artists
        ]
        return TrackResponse(
            id=new_track.id,
            title=new_track.title,
            isrc=new_track.isrc,
            genre=new_track.genre,
            label_id=new_track.label_id,
            label_share_percentage=new_track.label_share_percentage,
            scope_of_copyright=new_track.scope_of_copyright,
            scope_of_related_rights=new_track.scope_of_related_rights,
            neighboring_rights_share=new_track.neighboring_rights_share,
            label_rights_share=new_track.label_rights_share,
            label_monetization_share=new_track.label_monetization_share,
            marketing_expenses=new_track.marketing_expenses,
            advance_expenses=new_track.advance_expenses,
            is_ringtone_added=new_track.is_ringtone_added,
            has_video_clip=new_track.has_video_clip,
            is_lyrics_added=new_track.is_lyrics_added,
            is_karaoke_sync_added=new_track.is_karaoke_sync_added,
            text=new_track.text,
            karaoke=new_track.karaoke,
            synclab=new_track.synclab,
            copyright=new_track.copyright,
            related_rights=new_track.related_rights,
            advance=new_track.advance,
            marketing=new_track.marketing,
            album_id=new_track.album_id,
            artists=artists_resp,
            artist_ids=[a.id for a in new_track.artists],
            is_approved=new_track.is_approved
        )

    async def get_all_tracks(self) -> List[TrackResponse]:
        result = await self.db_session.execute(
            select(Track).where(Track.is_approved == True)
        )
        tracks = result.scalars().all()
        return await self._build_track_response_list(tracks)

    async def get_track_drafts(self, current_user: User) -> List[TrackResponse]:
        self._ensure_admin(current_user)
        result = await self.db_session.execute(
            select(Track).where(Track.is_approved == False)
        )
        drafts = result.scalars().all()
        return await self._build_track_response_list(drafts)

    async def _build_track_response_list(self, tracks) -> List[TrackResponse]:
        responses = []
        for track in tracks:
            album = await self.db_session.get(Album, track.album_id)
            track_artist_result = await self.db_session.execute(
                select(TrackArtist).where(TrackArtist.track_id == track.id)
            )
            artist_ids = [ta.artist_id for ta in track_artist_result.scalars().all()]
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
                TrackResponse(
                    id=track.id,
                    title=track.title,
                    isrc=track.isrc,
                    genre=track.genre,
                    label_id=track.label_id,
                    label_share_percentage=track.label_share_percentage,
                    scope_of_copyright=track.scope_of_copyright,
                    scope_of_related_rights=track.scope_of_related_rights,
                    neighboring_rights_share=track.neighboring_rights_share,
                    label_rights_share=track.label_rights_share,
                    label_monetization_share=track.label_monetization_share,
                    marketing_expenses=track.marketing_expenses,
                    advance_expenses=track.advance_expenses,
                    is_ringtone_added=track.is_ringtone_added,
                    has_video_clip=track.has_video_clip,
                    is_lyrics_added=track.is_lyrics_added,
                    is_karaoke_sync_added=track.is_karaoke_sync_added,
                    text=track.text,
                    karaoke=track.karaoke,
                    synclab=track.synclab,
                    copyright=track.copyright,
                    related_rights=track.related_rights,
                    advance=track.advance,
                    marketing=track.marketing,
                    album_id=track.album_id,
                    album_title=album.title if album else None,
                    artists=artists,
                    artist_ids=artist_ids,
                    is_approved=track.is_approved

                )
            )
        return responses

    async def approve_track_draft(self, track_id: int, current_user: User) -> TrackResponse:
        self._ensure_admin(current_user)
        track = await self._get_track_by_id(track_id)
        if track.is_approved:
            raise HTTPException(status_code=400, detail="Track is already approved")

        track.is_approved = True
        self.db_session.add(track)
        await self.db_session.commit()
        await self.db_session.refresh(track, ["album", "artists"])

        artists_resp = [
            ArtistResponse(
                id=a.id,
                name=a.name,
                isni=a.isni,
                is_approved=a.is_approved,
                created_by_user_id=a.created_by_user_id,
            )
            for a in track.artists
        ]
        return TrackResponse(
            id=track.id,
            title=track.title,
            isrc=track.isrc,
            genre=track.genre,
            label_id=track.label_id,
            label_share_percentage=track.label_share_percentage,
            scope_of_copyright=track.scope_of_copyright,
            scope_of_related_rights=track.scope_of_related_rights,
            neighboring_rights_share=track.neighboring_rights_share,
            label_rights_share=track.label_rights_share,
            label_monetization_share=track.label_monetization_share,
            marketing_expenses=track.marketing_expenses,
            advance_expenses=track.advance_expenses,
            is_ringtone_added=track.is_ringtone_added,
            has_video_clip=track.has_video_clip,
            is_lyrics_added=track.is_lyrics_added,
            is_karaoke_sync_added=track.is_karaoke_sync_added,
            text=track.text,
            karaoke=track.karaoke,
            synclab=track.synclab,
            copyright=track.copyright,
            related_rights=track.related_rights,
            advance=track.advance,
            marketing=track.marketing,
            album_id=track.album_id,
            artists=artists_resp,
            artist_ids=[a.id for a in track.artists],
            is_approved = track.is_approved
        )

    async def reject_track_draft(self, track_id: int, current_user: User) -> None:
        self._ensure_admin(current_user)
        track = await self._get_track_by_id(track_id)
        if track.is_approved:
            raise HTTPException(status_code=400, detail="Cannot reject already approved track")

        await self.db_session.execute(
            delete(TrackArtist).where(TrackArtist.track_id == track_id)
        )
        await self.db_session.execute(
            delete(TrackPersonShare).where(TrackPersonShare.track_id == track_id)
        )
        await self.db_session.delete(track)
        await self.db_session.commit()

    async def get_track_by_id(self, track_id: int, current_user: User) -> TrackDetailResponse:
        track = await self._get_track_by_id(track_id)

        if not track.is_approved and track.created_by_user_id != current_user.id and current_user.role != Role.ADMIN:
            raise HTTPException(status_code=404, detail="Track not found")

        album = await self.db_session.get(Album, track.album_id)
        album_resp = AlbumResponse(
            id=album.id,
            title=album.title,
            type=album.type,
            release_date=album.release_date,
            upc=album.upc,
            marketing_budget=album.marketing_expenses,
            advance=album.advance_expenses,
            aggregator=album.aggregator,
            yoga=album.Yoga,
            additional_sites=album.additional_sites,
            is_approved=track.is_approved
        ) if album else None

        track_artist_result = await self.db_session.execute(
            select(TrackArtist).where(TrackArtist.track_id == track_id)
        )
        artist_ids = [ta.artist_id for ta in track_artist_result.scalars().all()]
        artists = []
        if artist_ids:
            artists_result = await self.db_session.execute(
                select(Artist).where(Artist.id.in_(artist_ids))
            )
            artists_data = artists_result.scalars().all()
            artists = [
                ArtistDetailResponse(id=a.id, name=a.name, isni=a.isni, members=[])
                for a in artists_data
            ]

        shares_result = await self.db_session.execute(
            select(TrackPersonShare).where(TrackPersonShare.track_id == track_id)
        )
        shares = shares_result.scalars().all()
        track_person_shares = [
            TrackPersonShareResponse(
                person_id=share.person_id,
                share_author=share.share_of_monetization_of_copyrights,
                share_neighboring=share.share_of_monetization_of_related_rights,

            )
            for share in shares
        ]

        return TrackDetailResponse(
            id=track.id,
            title=track.title,
            isrc=track.isrc,
            genre=track.genre,
            music_authors=track.music_authors,
            lyrics_authors=track.lyrics_authors,
            scope_of_copyright=track.scope_of_copyright,
            scope_of_related_rights=track.scope_of_related_rights,
            neighboring_rights_share=track.neighboring_rights_share,
            label_rights_share=track.label_rights_share,
            label_monetization_share=track.label_monetization_share,
            artist_monetization_shares=track.artist_monetization_shares,
            marketing_expenses=track.marketing_expenses,
            advance_expenses=track.advance_expenses,
            advance=track.advance,
            marketing=track.marketing,
            text=track.text,
            karaoke=track.karaoke,
            synclab=track.synclab,
            copyright=track.copyright,
            related_rights=track.related_rights,
            is_ringtone_added=track.is_ringtone_added,
            has_video_clip=track.has_video_clip,
            is_lyrics_added=track.is_lyrics_added,
            is_karaoke_sync_added=track.is_karaoke_sync_added,
            album_id=track.album_id,
            artists=artists,
            track_person_shares=track_person_shares
        )

    async def update_track(
        self,
        track_id: int,
        data:TrackUpdateRequest,
        current_user: User
    ) -> TrackResponse:
        track = await self._get_track_by_id(track_id)

        if track.is_approved and current_user.role != Role.ADMIN:
            raise HTTPException(status_code=403, detail="Only admin can edit approved tracks")
        if not track.is_approved and track.created_by_user_id != current_user.id:
            raise HTTPException(status_code=403, detail="You can only edit your own drafts")

        if data.isrc is not None and data.isrc != track.isrc:
            exists = await self.db_session.execute(
                select(Track).where(Track.isrc == data.isrc, Track.is_approved == True)
            )
            if exists.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="ISRC already exists")

        if data.album_id is not None:
            album = await self.db_session.get(Album, data.album_id)
            if not album:
                raise HTTPException(status_code=400, detail="Album not found")

        if data.artist_ids is not None:
            if data.artist_ids:
                artist_result = await self.db_session.execute(
                    select(Artist).where(Artist.id.in_(data.artist_ids))
                )
                found = artist_result.scalars().all()
                if len(found) != len(data.artist_ids):
                    raise HTTPException(status_code=400, detail="Some artist IDs do not exist")

        update_data = data.model_dump(exclude_unset=True, exclude={'artist_ids'})
        for key, value in update_data.items():
            if hasattr(track, key):
                setattr(track, key, value)

        if data.artist_ids is not None:
            await self.db_session.execute(delete(TrackArtist).where(TrackArtist.track_id == track_id))
            for artist_id in data.artist_ids:
                self.db_session.add(TrackArtist(track_id=track.id, artist_id=artist_id))

        self.db_session.add(track)
        await self.db_session.commit()
        await self.db_session.refresh(track)

        return await self._build_track_response_list([track])[0]

    async def delete_track(self, track_id: int, current_user: User) -> bool:
        self._ensure_admin(current_user)
        track = await self._get_track_by_id(track_id)
        await self.db_session.execute(delete(TrackArtist).where(TrackArtist.track_id == track_id))
        await self.db_session.execute(delete(TrackPersonShare).where(TrackPersonShare.track_id == track_id))
        await self.db_session.delete(track)
        await self.db_session.commit()
        return True

# ✅ ФИНАЛЬНАЯ СТРОКА: только DBSessionDep
from typing import Annotated
from fastapi import Depends

TrackControllerDep = Annotated["TrackController", Depends(TrackController)]