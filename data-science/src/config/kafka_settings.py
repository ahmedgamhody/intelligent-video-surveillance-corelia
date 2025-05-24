from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator


class KafkaSettings(BaseSettings):
    IVS_KAFKA_PORT: int = 0000
    KAFKA_TOPIC: str = ""
    KAFKA_BROKER: str = ""

    model_config = SettingsConfigDict(env_file="../../.env", extra="ignore")

    @model_validator(mode="after")
    def set_app_root(self) -> "KafkaSettings":
        self.KAFKA_BROKER = f"localhost:{self.IVS_KAFKA_PORT}"
        return self
    