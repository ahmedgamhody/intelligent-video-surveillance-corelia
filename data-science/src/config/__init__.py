from .app_settings import AppSettings
from .db_settings import DBSettings
from .kafka_settings import KafkaSettings

app_settings = AppSettings()
db_settings = DBSettings()
kafka_settings = KafkaSettings()

NUM_PATCHES = 16