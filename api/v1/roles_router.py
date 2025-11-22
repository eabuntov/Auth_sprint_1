from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import UUID

from dependencies import get_role_service
from models.models import RoleRead, RoleCreate
from security.auth import require_permissions
from services.role_service import RoleService

roles_router = APIRouter(prefix="/roles", tags=["roles"])

@roles_router.post("/", response_model=RoleRead, dependencies=[Depends(require_permissions(["manage_roles"]))])
async def create_role(data: RoleCreate, roles: RoleService = Depends(get_role_service)):
    return await roles.create_role(data.name, data.permissions, data.description)

@roles_router.get("/", response_model=list[RoleRead])
async def list_roles(roles: RoleService = Depends(get_role_service)):
    return await roles.list_roles()

@roles_router.post("/{role_id}/assign/{user_id}")
async def assign_role(role_id: int, user_id: UUID, roles: RoleService = Depends(get_role_service)):
    try:
        await roles.assign_role(user_id=user_id, role_id=role_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return {"detail": "Role assigned"}

@roles_router.delete("/{role_id}/remove/{user_id}")
async def remove_role(role_id: int, user_id: UUID, roles: RoleService = Depends(get_role_service)):
    try:
        await roles.remove_role(user_id=user_id, role_id=role_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return {"detail": "Role removed"}
