-- Enable required TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Create surveillance table
CREATE TABLE IF NOT EXISTS surveillance (
    timestamp      TIMESTAMPTZ NOT NULL DEFAULT (now() AT TIME ZONE 'UTC'),
    channel_name   TEXT NOT NULL,
    source_name    TEXT NOT NULL,
    frame          TEXT,
    boxes          JSONB,
    masks          JSONB,
    keypoints      JSONB,
    frame_rate     FLOAT
);

-- Convert table to hypertable
SELECT create_hypertable('surveillance', 'timestamp', if_not_exists => TRUE);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_channel_timestamp ON surveillance(channel_name, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_source_timestamp ON surveillance(source_name, timestamp DESC);

-- run all by this commend:
-- psql -h localhost -p 5678 -U admin -d ivs -f ./api/src/datastores/services_storage/create_db.sql