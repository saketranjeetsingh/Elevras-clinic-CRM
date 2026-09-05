from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class RoleBase(BaseModel):
    name: str
    code: str


class RoleCreate(RoleBase):
    organization_id: Optional[int] = None


class RoleUpdate(BaseModel):
    name: Optional[str] = None


class RoleResponse(RoleBase):
    id: int
    organization_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class RoleWithPermissions(RoleResponse):
    permissions: List[str] = []


class PermissionBase(BaseModel):
    code: str
    description: Optional[str] = None


class PermissionCreate(PermissionBase):
    pass


class PermissionResponse(PermissionBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
