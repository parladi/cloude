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


def update_settings(server: str, port: int, user: str, password: str, database: str, database_backup: str):
    """Baglanti ayarlarini calisma zamaninda guncelle"""
    settings.DB_SERVER = server
    settings.DB_PORT = port
    settings.DB_USER = user
    settings.DB_PASSWORD = password
    settings.DB_NAME = database
    settings.DB_NAME_BACKUP = database_backup
