from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator


class AppSettings(BaseSettings):
    APP_NAME: str = ""
    APP_DESCRIPTION: str = ""
    DOMAIN: str = ""
    DEBUG_MODE: bool = False
    DATA_SCIENCE_PORT: int = 0000
    DATA_SCIENCE_VERSION: str = ""
    
    PORT: int = 0000
    ROOT: str = ""

    model_config = SettingsConfigDict(env_file="../../.env", extra="ignore")

    @model_validator(mode="after")
    def set_app_root(self) -> "AppSettings":
        self.PORT = self.DATA_SCIENCE_PORT
        self.ROOT = f"/{self.APP_NAME}/data-science/v{self.DATA_SCIENCE_VERSION.split(".")[0]}"
        return self
    