from pydantic import BaseSettings

class Settings(BaseSettings):
    secret_key: str = "supersecret"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 60 * 24 * 7

settings = Settings()
