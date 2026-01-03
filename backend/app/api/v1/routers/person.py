from fastapi import APIRouter, Depends
from starlette import status

from app.api.v1.models.person import PersonCreateRequest, PersonResponse, PersonUpdateRequest
from app.api.v1.controllers.person import PersonControllerDep
from app.deps import AuthUserDep
from app.sqlmodels.user import User

router = APIRouter(prefix="/people", tags=["people"])

@router.post("/", response_model=PersonResponse)
async def create_person(
    data: PersonCreateRequest,
    controller: PersonControllerDep,
    current_user: AuthUserDep,
) -> PersonResponse:
    return await controller.create_person(data, current_user)

@router.get("/", response_model=list[PersonResponse])
async def list_people(
    controller: PersonControllerDep,
) -> list[PersonResponse]:
    return await controller.get_all_people()

@router.put("/{person_id}", response_model=PersonResponse)
async def update_person(
    person_id: int,
    data: PersonUpdateRequest,
    controller: PersonControllerDep,
    current_user: User = Depends(AuthUserDep),
) -> PersonResponse:
    return await controller.update_person(person_id, data, current_user)

@router.get("/{person_id}", response_model=PersonResponse)
async def get_person(
    person_id: int,
    controller: PersonControllerDep,
    current_user: User = Depends(AuthUserDep),
) -> PersonResponse:
    return await controller.get_person_by_id(person_id, current_user)

@router.delete("/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_person(
    person_id: int,
    controller: PersonControllerDep,
    current_user: AuthUserDep,
) -> None:
    await controller.delete_person(person_id, current_user)

