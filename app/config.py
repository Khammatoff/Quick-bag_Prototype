from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    # JWT Настройки
    SECRET_KEY: str = Field("your-secret-key", env="SECRET_KEY")  # Замените в production!
    ALGORITHM: str = Field("HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # Настройки БД
    DEBUG: bool = Field(True, env="DEBUG")
    DB_HOST: str = Field("db", env="DB_HOST")
    DB_USER: str = Field("user", env="DB_USER")
    DB_PASSWORD: str = Field("password", env="DB_PASSWORD")
    DB_NAME: str = Field("foodbasket", env="DB_NAME")
    DB_PORT: int = Field(3306, env="DB_PORT")

    # Настройки API
    API_V1_STR: str = Field("/api/v1", env="API_V1_STR")

    SWAGGER_CLIENT_ID: Optional[str] = Field(None, env="SWAGGER_CLIENT_ID")
    SWAGGER_CLIENT_SECRET: Optional[str] = Field(None, env="SWAGGER_CLIENT_SECRET")

    @property
    def database_url(self) -> str:
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Игнорируем лишние переменные из .env


settings = Settings()
