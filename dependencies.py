from typing import AsyncGenerator

from redis import Redis
from fastapi import Depends

from repositories.user_repository import UserRepository
from repositories.roles_repository import RoleRepository
from repositories.subscription_repository import SubscriptionRepository
from security.password import PasswordHasher
from services.user_service import UserService
from services.role_service import RoleService
from services.subscription_service import SubscriptionService
from services.token_service import TokenService
from security.jwt_routines import JWTHandler



from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from config.settings import settings


# Create PostgreSQL async engine
engine = create_async_engine(
    settings.database_url,
    echo=bool(settings.db_echo),
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


# Dependency for FastAPI
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def get_redis() -> Redis:
    return Redis.from_url(settings.REDIS_URL, decode_responses=True)


def get_user_repo(session: AsyncSession = Depends(get_session)) -> UserRepository:
    return UserRepository(session)


def get_role_repo(session: AsyncSession = Depends(get_session)) -> RoleRepository:
    return RoleRepository(session)


def get_subscription_repo(
    session: AsyncSession = Depends(get_session),
) -> SubscriptionRepository:
    return SubscriptionRepository(session)


# ---------------------- SERVICES ----------------------
def get_user_service(repo: UserRepository = Depends(get_user_repo)) -> UserService:
    return UserService(repo, PasswordHasher())


def get_role_service(repo: RoleRepository = Depends(get_role_repo)) -> RoleService:
    return RoleService(repo)


def get_subscription_service(
    repo: SubscriptionRepository = Depends(get_subscription_repo),
) -> SubscriptionService:
    return SubscriptionService(repo)


def get_token_service(
    redis: Redis = Depends(get_redis),
    user_repo: UserRepository = Depends(get_user_repo),
) -> TokenService:
    return TokenService(JWTHandler(), redis, user_repo)


# ---------------------- AUTHENTICATION ----------------------
from security.auth import AuthBearer, get_current_user, require_permissions  # noqa
