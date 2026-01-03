from fastapi import APIRouter, Depends, status
from app.deps import AdminUserDep # ← Pydantic-модель

# Controllers
from app.api.v1.controllers.person import PersonControllerDep
from app.api.v1.controllers.track import TrackControllerDep
from app.api.v1.controllers.artist import ArtistControllerDep
from app.api.v1.controllers.album import AlbumControllerDep

# Response models
from app.api.v1.models.person import PersonResponse
from app.api.v1.models.track import TrackResponse
from app.api.v1.models.artist import ArtistDetailResponse, ArtistResponse
from app.api.v1.models.album import AlbumDetailResponse, AlbumResponse

router = APIRouter(prefix="/drafts", tags=["Drafts"])


# =============== PERSONS ===============

@router.get("/persons", response_model=list[PersonResponse])
async def get_person_drafts(
    controller: PersonControllerDep,
    user: AdminUserDep,  # ← как в твоём примере!
) -> list[PersonResponse]:
    return await controller.get_person_drafts(user)


@router.patch("/persons/{person_id}/approve", response_model=PersonResponse)
async def approve_person_draft(
    person_id: int,
    controller: PersonControllerDep,
    user: AdminUserDep,
) -> PersonResponse:
    return await controller.approve_person_draft(person_id, user)


@router.delete("/persons/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
async def reject_person_draft(
    person_id: int,
    controller: PersonControllerDep,
    user: AdminUserDep,
) -> None:
    await controller.reject_person_draft(person_id, user)


# =============== TRACKS ===============

@router.get("/tracks", response_model=list[TrackResponse])
async def get_track_drafts(
    controller: TrackControllerDep,
    user: AdminUserDep,
) -> list[TrackResponse]:
    return await controller.get_track_drafts(user)


@router.patch("/tracks/{track_id}/approve", response_model=TrackResponse)
async def approve_track_draft(
    track_id: int,
    controller: TrackControllerDep,
    user: AdminUserDep,
) -> TrackResponse:
    return await controller.approve_track_draft(track_id, user)


@router.delete("/tracks/{track_id}", status_code=status.HTTP_204_NO_CONTENT)
async def reject_track_draft(
    track_id: int,
    controller: TrackControllerDep,
    user: AdminUserDep,
) -> None:
    await controller.reject_track_draft(track_id, user)


# =============== ARTISTS ===============

@router.get("/artists", response_model=list[ArtistDetailResponse])
async def get_artist_drafts(
    controller: ArtistControllerDep,
    user: AdminUserDep,  # ← теперь передаётся!
) -> list[ArtistDetailResponse]:
    return await controller.get_artist_drafts(user)  # ← передаём user


@router.patch("/artists/{artist_id}/approve", response_model=ArtistResponse)
async def approve_artist_draft(
    artist_id: int,
    controller: ArtistControllerDep,
    user: AdminUserDep,
) -> ArtistResponse:
    return await controller.approve_artist_draft(artist_id, user)


@router.delete("/artists/{artist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def reject_artist_draft(
    artist_id: int,
    controller: ArtistControllerDep,
    user: AdminUserDep,
) -> None:
    await controller.reject_artist_draft(artist_id, user)


# =============== ALBUMS ===============

@router.get("/albums", response_model=list[AlbumDetailResponse])
async def get_album_drafts(
    controller: AlbumControllerDep,
    user: AdminUserDep,
) -> list[AlbumDetailResponse]:
    return await controller.get_album_drafts(user)


@router.patch("/albums/{album_id}/approve", response_model=AlbumResponse)
async def approve_album_draft(
    album_id: int,
    controller: AlbumControllerDep,
    user: AdminUserDep,
) -> AlbumResponse:
    return await controller.approve_album_draft(album_id, user)


@router.delete("/albums/{album_id}", status_code=status.HTTP_204_NO_CONTENT)
async def reject_album_draft(
    album_id: int,
    controller: AlbumControllerDep,
    user: AdminUserDep,
) -> None:
    await controller.reject_album_draft(album_id, user)