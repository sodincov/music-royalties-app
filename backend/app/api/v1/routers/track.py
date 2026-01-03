# app/api/v1/routers/track.py
from fastapi import APIRouter, status, Depends
from app.api.v1.models.track import TrackResponse, TrackDetailResponse, TrackUpdateRequest, TrackCreateRequest
from app.api.v1.controllers.track import TrackControllerDep
from app.deps import AuthUserDep
from app.sqlmodels.user import User

router = APIRouter(prefix="/tracks", tags=["tracks"])

@router.post("/", response_model=TrackResponse)
async def create_track(
    data:TrackCreateRequest,
    controller: TrackControllerDep,
    current_user: AuthUserDep,
) -> TrackResponse:
    return await controller.create_track(data, current_user)

@router.get("/", response_model=list[TrackResponse])
async def list_tracks(
    controller: TrackControllerDep,
) -> list[TrackResponse]:
    return await controller.get_all_tracks()

@router.get("/{track_id}", response_model=TrackDetailResponse)
async def get_track(
    track_id: int,
    controller: TrackControllerDep,
    current_user: AuthUserDep,
) -> TrackDetailResponse:
    return await controller.get_track_by_id(track_id, current_user)

@router.put("/{track_id}", response_model=TrackResponse)
async def update_track(
    track_id: int,
    data:TrackUpdateRequest,
    controller: TrackControllerDep,
    current_user: AuthUserDep,
) -> TrackResponse:
    return await controller.update_track(track_id, data, current_user)

@router.delete("/{track_id}")
async def delete_track(
    track_id: int,
    controller: TrackControllerDep,
    current_user: AuthUserDep,
) -> bool:
    return await controller.delete_track(track_id, current_user)
