import json
import asyncio
from aiokafka import AIOKafkaConsumer
from config import kafka_settings as kfs

class KafkaConsumerService:
    def __init__(self, db_controller):
        self.consumer: AIOKafkaConsumer = None
        self.db_controller = db_controller
        self.started = False
        self._consume_task = None

    async def start(self):
        if self.started:
            return

        self.consumer = AIOKafkaConsumer(
            kfs.KAFKA_TOPIC,
            bootstrap_servers=kfs.KAFKA_BROKER,
            group_id='ivs-consumers',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='latest',
            enable_auto_commit=True,
            session_timeout_ms=60000,
            max_poll_interval_ms=30000,
            heartbeat_interval_ms=15000
        )
        await self.consumer.start()
        self.started = True
        self._consume_task = asyncio.create_task(self.consume())
        print("✅ AIOKafkaConsumer started")

    async def stop(self):
        if self.consumer:
            await self.consumer.stop()
            print("🛑 AIOKafkaConsumer stopped")
        if self._consume_task:
            self._consume_task.cancel()
        self.started = False

    async def consume(self):
        try:
            async for msg in self.consumer:
                message = msg.value
                channel = message.get("channel_name")
                data = message.get("data")
                if channel and data:
                    asyncio.create_task(self.db_controller.push(channel, data))
                    # print(f"📥 Consumed from Kafka: {channel} | {len(data)} items")
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"❌ Kafka consume error: {e}")
