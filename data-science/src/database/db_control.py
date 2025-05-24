import asyncpg
import json
from datetime import datetime
from typing import List

class DBControl:
    def __init__(self, dbs):
        self.dsn = f"postgresql://{dbs.IVS_SERVICE_DB_USER}:{dbs.IVS_SERVICE_DB_PASS}@localhost:{dbs.IVS_SERVICE_DB_PORT}/{dbs.IVS_SERVICE_DB_NAME}"
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(dsn=self.dsn)
        print("✅ Predictor Database connected")

    async def disconnect(self):
        if self.pool:
            await self.pool.close()
            self.pool = None
            print("🛑 Predictor Databse disconnected")

    async def push(self, channel_name: str, data: List[dict]):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                for item in data:
                    query = """
                        INSERT INTO surveillance (channel_name, source_name, frame, boxes, masks, keypoints, frame_rate)
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                    """
                    await conn.execute(query, channel_name, item['source_name'], item['frame'], 
                                       json.dumps(item['boxes']), json.dumps(item['masks']), json.dumps(item['keypoints']), item['frame_rate'])

    async def get(self, channel_name: str, start: datetime, end: datetime) -> list[dict]:
        async with self.pool.acquire() as conn:
            query = """
                SELECT timestamp, json_agg(json_build_object(
                    'source_name', source_name,
                    'frame', frame,
                    'boxes', boxes,
                    'masks', masks,
                    'keypoints', keypoints,
                    'frame_rate', frame_rate
                )) as data
                FROM surveillance
                WHERE channel_name = $1 AND timestamp BETWEEN $2 AND $3
                GROUP BY timestamp
                ORDER BY timestamp
            """
            rows = await conn.fetch(query, channel_name, start, end)
            return [{"timestamp": row["timestamp"].isoformat(), "data": json.loads(row["data"])} for row in rows]

    async def pull(self, channel_name: str, more_instances: int = 0) -> list[dict]:
        async with self.pool.acquire() as conn:
            query = """
                WITH params AS (
                    SELECT 
                        MAX(timestamp) as latest_ts,
                        MAX(timestamp) - make_interval(secs => $2) as historical_start
                    FROM surveillance 
                    WHERE channel_name = $1
                ),
                latest_data AS (
                    SELECT 
                        timestamp,
                        json_agg(json_build_object(
                            'source_name', source_name,
                            'frame', frame,
                            'boxes', boxes,
                            'masks', masks,
                            'keypoints', keypoints,
                            'frame_rate', frame_rate
                        )) as data
                    FROM surveillance, params
                    WHERE channel_name = $1 
                    AND timestamp = params.latest_ts
                    GROUP BY timestamp
                ),
                historical_data AS (
                    SELECT 
                        timestamp,
                        json_agg(json_build_object(
                            'source_name', source_name,
                            'boxes', boxes
                        )) as data
                    FROM surveillance, params
                    WHERE channel_name = $1 
                    AND timestamp >= params.historical_start 
                    AND timestamp < params.latest_ts
                    GROUP BY timestamp
                )
                SELECT * FROM latest_data
                UNION ALL
                SELECT * FROM historical_data
                ORDER BY timestamp DESC
            """
            rows = await conn.fetch(query, channel_name, more_instances)
            return [{"timestamp": row["timestamp"].isoformat(), "data": json.loads(row["data"])} for row in rows]