import json
from aiokafka import AIOKafkaProducer
from config import kafka_settings as kfs


class KafkaProducerService:
    def __init__(self, kafka_topic=kfs.KAFKA_TOPIC, bootstrap_servers=kfs.KAFKA_BROKER):
        self._producer: AIOKafkaProducer = None
        self.kafka_topic = kafka_topic
        self.bootstrap_servers = bootstrap_servers

    async def start(self):
        self._producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )
        await self._producer.start()
        print("✅ AIOKafkaProducer started")

    async def stop(self):
        if self._producer:
            await self._producer.stop()
            print("🛑 AIOKafkaProducer stopped")

    async def push(self, channel_name: str, data: list):
        if not self._producer:
            raise RuntimeError("Kafka producer is not initialized. Call `start()` first.")

        message = {
            "channel_name": channel_name,
            "data": data
        }

        try:
            await self._producer.send_and_wait(self.kafka_topic, message)
            # print(f"✅ Sent to Kafka: {channel_name} | {len(data)} items")
        except Exception as e:
            print(f"❌ Kafka send error: {e}")
