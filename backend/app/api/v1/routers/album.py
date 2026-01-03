# app/api/v1/routers/album.py
from fastapi import APIRouter, status, Depends
from app.api.v1.models.album import AlbumCreateRequest, AlbumResponse, AlbumDetailResponse, AlbumUpdateRequest
from app.api.v1.controllers.album import AlbumControllerDep
from app.deps import AuthUserDep
from app.sqlmodels.user import User

router = APIRouter(prefix="/albums", tags=["albums"])

@router.post("/", response_model=AlbumResponse)
async def create_album(
    data:AlbumCreateRequest,
    controller: AlbumControllerDep,
    current_user: User = Depends(AuthUserDep),
) -> AlbumResponse:
    return await controller.create_album(data, current_user)

@router.get("/", response_model=list[AlbumDetailResponse])
async def list_albums(
    controller: AlbumControllerDep,
) -> list[AlbumDetailResponse]:
    return await controller.get_all_albums()

@router.get("/{album_id}", response_model=AlbumDetailResponse)
async def get_album(
    album_id: int,
    controller: AlbumControllerDep,
    current_user: User = Depends(AuthUserDep),
) -> AlbumDetailResponse:
    return await controller.get_album_by_id(album_id, current_user)

@router.put("/{album_id}", response_model=AlbumResponse)
async def update_album(
    album_id: int,
    data:AlbumUpdateRequest,
    controller: AlbumControllerDep,
    current_user: User = Depends(AuthUserDep),
) -> AlbumResponse:
    return await controller.update_album(album_id, data, current_user)

@router.delete("/{album_id}")
async def delete_album(
    album_id: int,
    controller: AlbumControllerDep,
    current_user: User = Depends(AuthUserDep),
) -> bool:
    return await controller.delete_album(album_id, current_user)
