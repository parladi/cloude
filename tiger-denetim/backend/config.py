from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_SERVER: str = "192.168.0.9"
    DB_PORT: int = 1433
    DB_USER: str = "sa"
    DB_PASSWORD: str = ""
    DB_NAME: str = "TIGERDB"
    DB_NAME_BACKUP: str = "VeribanLocalDB"

    class Config:
        env_file = ".env"


settings = Settings()
