from pydantic_settings import BaseSettings, SettingsConfigDict


class DBSettings(BaseSettings):
    IVS_SERVICE_DB_PORT: int = 0000
    IVS_SERVICE_DB_NAME: str = ""
    IVS_SERVICE_DB_USER: str = ""
    IVS_SERVICE_DB_PASS: str = ""

    model_config = SettingsConfigDict(env_file="../../.env", extra="ignore")
