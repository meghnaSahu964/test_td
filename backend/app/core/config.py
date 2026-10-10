from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "postgresql+psycopg://amba:change-me@localhost:5432/amba"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "development-only-change-me"
    jwt_refresh_secret: str = "development-only-change-me-refresh"
    access_token_expire_minutes: int = 30
    frontend_url: str = "http://localhost:3000"
    business_email: str = "hr@ambarealestate.co.in"
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from: str | None = None
    storage_provider: str = "local"
settings = Settings()
