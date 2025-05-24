from pydantic_settings import BaseSettings, SettingsConfigDict


class DBSettings(BaseSettings):
    IVS_SYSTEM_DB_PORT: int = 0
    IVS_SYSTEM_DB_NAME: str = ""
    IVS_SYSTEM_DB_USER: str = ""
    IVS_SYSTEM_DB_PASS: str = ""

    model_config = SettingsConfigDict(env_file="../../.env", extra="ignore")
