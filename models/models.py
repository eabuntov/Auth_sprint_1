"""
Authentication & Authorization Service
--------------------------------------
File: auth_service_models.py

This file contains:
- High-level architecture notes for a JWT-based AuthZ service implemented with FastAPI.
- Pydantic data models (request/response/DTOs) that the service API will expose.

Architecture (brief)
--------------------
Components:
  - FastAPI app exposing REST endpoints for authentication, token lifecycle, user management, and role management.
  - Postgres (or another relational DB) for persistent storage of users, roles, subscriptions, and assignments.
  - Redis for: token revocation list, short-lived caches, and session/refresh token rotation metadata.
  - Optional: an internal JWKS endpoint that exposes the public key (if using asymmetric JWTs) so other services can verify tokens without contacting the auth service on each request.
  - Other services (cinema public API, admin panel) verify access tokens locally (via JWKS or shared secret) and call the auth service for user/role introspection if needed.

Key design choices:
  - Access tokens (JWTs) are short-lived (e.g. 5-15 minutes). Refresh tokens are long-lived (days/weeks) and stored server-side (or their rotation state is tracked) to allow revocation.
  - Use token rotation for refresh tokens to limit replay attacks. Store refresh token identifiers (jti) in Redis with state (valid/revoked).
  - Roles are collections of permissions. Users get roles via assignments. Roles CRUD endpoints exist and are protected to admins.
  - Anonymous users exist implicitly: when no auth header provided, treat user as `anonymous` role with minimal permissions.
  - Superuser flag or role grants all rights.
  - Subscriptions are first-class objects that grant additional permissions/entitlements (e.g. access to certain movie content). Subscription evaluation may be done by other services using token claims (e.g. `entitlements` array) or via an introspection endpoint.

Security notes (short):
  - Use HTTPS for all traffic.
  - Store password hashes (bcrypt/argon2) only.
  - Keep refresh token identifiers in Redis, not raw refresh tokens; issue a secure opaque refresh token bound to that id.
  - Rotate keys and support key identifiers (kid) in JWT headers when using asymmetric signing.


Pydantic models
---------------
"""

from enum import Enum
from typing import Optional
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr, Field


class Permission(str, Enum):
    # general app permissions (extend as needed)
    READ_PUBLIC_CONTENT = "read:public_content"
    WATCH_MOVIES = "watch:movies"
    MANAGE_USERS = "manage:users"
    MANAGE_ROLES = "manage:roles"
    MANAGE_SUBSCRIPTIONS = "manage:subscriptions"
    VIEW_ADMIN_PANEL = "view:admin_panel"
    # add app specific permissions below


class RoleType(str, Enum):
    DEFAULT = "default"
    ADMIN = "admin"
    SYSTEM = "system"


class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int  # seconds until access token expiration


class TokenPayload(BaseModel):
    sub: str  # subject: user id (UUID or DB id represented as string)
    exp: int
    iat: int
    jti: Optional[str] = None
    scopes: Optional[list[str]] = []
    roles: Optional[list[str]] = []
    entitlements: Optional[list[str]] = []


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserRead(UserBase):
    id: UUID
    roles: list[str] = []
    subscriptions: list[str] = []  # subscription ids or names
    created_at: datetime
    updated_at: Optional[datetime] = None


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8)

class PasswordChange(BaseModel):
    old_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)


class UserTokenInfo(BaseModel):
    sub: str
    email: EmailStr
    roles: list[str] = []
    entitlements: list[str] = []
    is_superuser: bool = False


class LoginRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: Optional[str] = None
    access_jti: Optional[str] = None


class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)


class RoleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    permissions: set[Permission] = set()
    type: RoleType = RoleType.DEFAULT


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    description: Optional[str] = None
    permissions: Optional[set[Permission]] = None
    type: Optional[RoleType] = None


class RoleRead(RoleBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None


class RoleApplyRequest(BaseModel):
    user_id: UUID
    role_id: UUID
    expires_at: Optional[datetime] = None  # temporary role assignment


class RoleAssignmentRead(BaseModel):
    id: UUID
    role_id: UUID
    user_id: UUID
    assigned_by: Optional[UUID] = None
    expires_at: Optional[datetime] = None
    created_at: datetime


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class SubscriptionBase(BaseModel):
    name: str
    description: Optional[str] = None
    # entitlements optionally granted by this subscription (e.g. "hd-stream", "catalog-premium")
    entitlements: set[str] = set()
    duration_days: Optional[int] = (
        None  # if recurring, this may be null/managed externally
    )


class SubscriptionCreate(SubscriptionBase):
    price_cents: Optional[int] = None


class SubscriptionRead(SubscriptionBase):
    id: UUID
    status: SubscriptionStatus
    user_id: UUID
    started_at: datetime
    ends_at: Optional[datetime] = None


class RightsCheckRequest(BaseModel):
    user_id: Optional[UUID] = None
    token: Optional[str] = None
    required_permissions: Optional[set[Permission]] = None
    required_entitlements: Optional[set[str]] = None


class RightsCheckResponse(BaseModel):
    allowed: bool
    missing_permissions: list[Permission] = []
    missing_entitlements: list[str] = []
    reason: Optional[str] = None


class PagedMeta(BaseModel):
    total: int
    page: int
    size: int


class PagedResponse(BaseModel):
    meta: PagedMeta
    items: list[BaseModel]


def make_access_token_payload(
    user_id: str,
    roles: list[str],
    entitlements: list[str],
    expires_delta_seconds: int,
    jti: Optional[str] = None,
) -> TokenPayload:
    now = datetime.now()
    iat = int(now.timestamp())
    exp = int((now + timedelta(seconds=expires_delta_seconds)).timestamp())
    return TokenPayload(
        sub=user_id,
        iat=iat,
        exp=exp,
        jti=jti or str(uuid4()),
        roles=roles,
        scopes=[],
        entitlements=entitlements,
    )
