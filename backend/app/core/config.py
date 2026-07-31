from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central application configuration.
    All values are read from environment variables (or a .env file locally).
    Never hardcode secrets here — in Kubernetes these come from a Secret,
    in local docker-compose they come from the .env file.
    """

    PROJECT_NAME: str = "Clinic Booking System"
    API_V1_PREFIX: str = "/api/v1"

    # Database
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "clinic_user"
    POSTGRES_PASSWORD: str = "change_me"
    POSTGRES_DB: str = "clinic_db"

    # JWT
    SECRET_KEY: str = "change_this_secret_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS - comma separated origins in env, e.g. "https://app.example.com,https://example.com"
    CORS_ORIGINS: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
