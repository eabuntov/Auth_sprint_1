from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # ---------------------- DATABASE ----------------------
    DATABASE_URL: str = Field(..., env="DATABASE_URL")

    # ---------------------- REDIS ----------------------
    REDIS_URL: str = Field(..., env="REDIS_URL")

    # ---------------------- JWT ----------------------
    JWT_ACCESS_SECRET: str = Field(..., env="JWT_ACCESS_SECRET")
    JWT_REFRESH_SECRET: str = Field(..., env="JWT_REFRESH_SECRET")
    JWT_ALGORITHM: str = Field("HS256", env="JWT_ALGORITHM")

    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(15, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(30, env="REFRESH_TOKEN_EXPIRE_DAYS")

    # ---------------------- PASSWORD HASHING ----------------------
    BCRYPT_ROUNDS: int = Field(12, env="BCRYPT_ROUNDS")

    # ---------------------- APP SETTINGS ----------------------
    DEBUG: bool = Field(False, env="DEBUG")
    PROJECT_NAME: str = "Auth Service"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
