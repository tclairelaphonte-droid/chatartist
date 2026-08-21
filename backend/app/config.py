from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Base de données
    database_url: str = (
        "postgresql+psycopg2://backstage_user:backstage_pw"
        "@localhost:5432/backstage"
    )

    # JWT
    jwt_secret: str = "change-moi-en-production"
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "backstage-api"
    jwt_audience: str = "backstage-client"
    access_token_expire_minutes: int = 60 * 24 * 7

   # Uploads
max_upload_size_mb: int = 5
    # CORS
    cors_origins: list[str] = [
        "https://chatartist-frontend.vercel.app",
        "http://192.168.1.1:5741",
        "http://localhost:5741",
        "http://127.0.0.1:5741",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="BACKSTAGE_",
        extra="ignore",
    )


settings = Settings()