from fastapi import APIRouter, Depends

from models.models import RoleRead, RoleCreate
from services.role_service import RoleService

roles_router = APIRouter(prefix="/roles", tags=["roles"])

@roles_router.post("/", response_model=RoleRead, dependencies=[Depends(require_permissions(["manage_roles"]))])
async def create_role(data: RoleCreate, roles: RoleService = Depends(get_role_service)):
    return await roles.create(data)

@roles_router.get("/", response_model=list[RoleRead])
async def list_roles(roles: RoleService = Depends(get_role_service)):
    return await roles.list()

@roles_router.post("/{role_id}/assign/{user_id}")
async def assign_role(role_id: int, user_id: int, roles: RoleService = Depends(get_role_service)):
    await roles.assign_role(user_id, role_id)
    return {"detail": "Role assigned"}

@roles_router.delete("/{role_id}/remove/{user_id}")
async def remove_role(role_id: int, user_id: int, roles: RoleService = Depends(get_role_service)):
    await roles.remove_role(user_id, role_id)
    return {"detail": "Role removed"}