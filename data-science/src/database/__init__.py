from config import db_settings as dbs
from .db_control import DBControl
from .kafka_consumer import KafkaConsumerService
from .kafka_producer import KafkaProducerService


db_controller = DBControl(dbs)
kafka_consumer = KafkaConsumerService(db_controller)
kafka_producer = KafkaProducerService()