from fastapi import APIRouter, Depends, Response, status

from app.api.v1.models.user import UserResponse
from app.deps import AuthUserDep
from app.api.v1.models.artist import (
    ArtistCreateRequest,
    ArtistResponse,
    ArtistDetailResponse,
    ArtistUpdateRequest
)
from app.api.v1.controllers.artist import ArtistControllerDep

router = APIRouter(prefix="/artists", tags=["artists"])


@router.post("/", response_model=ArtistResponse)
async def create_artist(
    data:ArtistCreateRequest,
    controller: ArtistControllerDep,
    current_user: AuthUserDep,
    response: Response = None,
) -> ArtistResponse:
    artist = await controller.create_artist(data, current_user)
    if not artist.is_approved:
        response.status_code = 202  # Accepted (draft)
    return artist


@router.get("/", response_model=list[ArtistDetailResponse])
async def list_artists(
    controller: ArtistControllerDep,
    current_user: AuthUserDep,
) -> list[ArtistDetailResponse]:
    return await controller.get_all_artists()


@router.get("/{artist_id}", response_model=ArtistDetailResponse)
async def get_artist(
    artist_id: int,
    controller: ArtistControllerDep,
    current_user: AuthUserDep,
) -> ArtistDetailResponse:
    return await controller.get_artist_by_id(artist_id, current_user)


@router.put("/{artist_id}", response_model=ArtistResponse)
async def update_artist(
    artist_id: int,
    data:ArtistUpdateRequest,
    controller: ArtistControllerDep,
    current_user: AuthUserDep,
) -> ArtistResponse:
    return await controller.update_artist(artist_id, data, current_user)


@router.delete("/{artist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_artist(
    artist_id: int,
    controller: ArtistControllerDep,
    current_user: AuthUserDep,
) -> None:
    await controller.delete_artist(artist_id, current_user)