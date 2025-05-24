from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator


class AppSettings(BaseSettings):
    APP_NAME: str = ""
    APP_DESCRIPTION: str = ""
    DOMAIN: str = ""
    DEBUG_MODE: bool = False
    BACKEND_PORT: int = 0000
    BACKEND_VERSION: str = ""

    PORT: int = 0000
    ROOT: str = ""

    model_config = SettingsConfigDict(env_file="../../.env", extra="ignore")

    @model_validator(mode="after")
    def set_app_root(self) -> "AppSettings":
        self.PORT = self.BACKEND_PORT
        self.ROOT = f"/{self.APP_NAME}/backend/v{self.BACKEND_VERSION.split('.')[0]}"
        return self
    