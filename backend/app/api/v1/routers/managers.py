from fastapi import APIRouter, Depends

from app.api.v1.controllers.managers import UserControllerDep
from app.api.v1.models.manager import ManagerResponse
from app.api.v1.models.user import ManagerCreateRequest
from app.deps import AdminUserDep

router = APIRouter(prefix="/managers", tags=["managers"])

@router.post("/", response_model=ManagerResponse)
async def create_manager(
    data: ManagerCreateRequest,
    user: AdminUserDep,
    controller: UserControllerDep,
)->ManagerResponse:
    return await controller.create_manager(data=data, user=user)


@router.get("/", response_model=list[ManagerResponse])
async def get_managers(
        controller: UserControllerDep
) -> list[ManagerResponse]:
    return await controller.get_all_managers()

@router.delete("/{manager_id}")
async def deactivate_manager(
    manager_id: int,
    user: AdminUserDep,  # Проверяем, что пользователь - админ
    controller: UserControllerDep,
):
    await controller.deactivate_manager(manager_id=manager_id, admin_user=user)
    return {"message": "Manager deactivated successfully"}