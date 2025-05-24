-- Enable citext extension
CREATE EXTENSION IF NOT EXISTS citext;

-- ENUM Types
CREATE TYPE enum_user_role AS ENUM ('admin', 'editor', 'viewer');
CREATE TYPE enum_running_status AS ENUM ('active', 'pending', 'inactive');
CREATE TYPE enum_model_task AS ENUM ('detection', 'segmentation', 'estimation');
CREATE TYPE enum_model_weight AS ENUM ('nano', 'small', 'medium', 'large', 'x-large');
CREATE TYPE enum_log_action AS ENUM ('create', 'update', 'delete');

-- Table: users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email CITEXT UNIQUE NOT NULL,
    password BYTEA NOT NULL,
    role enum_user_role NOT NULL DEFAULT 'viewer'
);

-- Table: channels
CREATE TABLE channels (
    id SERIAL PRIMARY KEY,
    name CITEXT UNIQUE NOT NULL,
    status enum_running_status DEFAULT 'active',

    -- processing configurations
    confidence INT NOT NULL,
    overlapping INT NOT NULL,
    realtime BOOLEAN NOT NULL,
    augmentation BOOLEAN NOT NULL,
    tracking BOOLEAN NOT NULL,
    reid BOOLEAN NOT NULL,

    -- plotting configurations as JSONB
    plotting_config JSONB NOT NULL DEFAULT '{
        "history": 0,

        "plot_source_name": false,
        "plot_date_time": false,
        "plot_frame_rate": false,
    
        "plot_classes_counts": true,
        "plot_classes_summations": true,
    
        "plot_classes": true,
        "plot_tracking_ids": true,
        "plot_objects_durations": true,
        
        "plot_boxes": true,
        "plot_masks": true,
        "plot_keypoints": true,
    
        "plot_confidence": false,
    
        "plot_tracking_lines": false,
        "plot_heat_map": false,
        "plot_blur": false
    }'::JSONB
);

-- Table: sources
CREATE TABLE sources (
    id SERIAL PRIMARY KEY,
    channel_id INTEGER REFERENCES channels(id),
    name CITEXT NOT NULL,
    url TEXT NOT NULL,
    status enum_running_status DEFAULT 'active',

    CONSTRAINT unique_source_name_per_channel UNIQUE (channel_id, name)
);

-- Table: models
CREATE TABLE models (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    task enum_model_task NOT NULL,
    weight enum_model_weight NOT NULL,
    classes JSONB
);

-- Table: channels_users (many-to-many)
CREATE TABLE channels_users (
    channel_id INTEGER REFERENCES channels(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    PRIMARY KEY (channel_id, user_id)
);

-- Table: channels_models (many-to-many)
CREATE TABLE channels_models (
    channel_id INTEGER REFERENCES channels(id) ON DELETE CASCADE,
    model_id INTEGER REFERENCES models(id) ON DELETE CASCADE,
    PRIMARY KEY (channel_id, model_id)
);

-- Table: users_logs
CREATE TABLE users_logs (
    id SERIAL PRIMARY KEY,
    performed_by INTEGER REFERENCES users(id),
    performed_at TIMESTAMPTZ DEFAULT NOW(),
    user_id INTEGER REFERENCES users(id),
    action enum_log_action NOT NULL,
    details JSONB
);

-- Table: channels_logs
CREATE TABLE channels_logs (
    id SERIAL PRIMARY KEY,
    performed_by INTEGER REFERENCES users(id),
    performed_at TIMESTAMPTZ DEFAULT NOW(),
    channel_id INTEGER REFERENCES channels(id),
    action enum_log_action NOT NULL,
    details JSONB
);

-- Table: sources_logs
CREATE TABLE sources_logs (
    id SERIAL PRIMARY KEY,
    performed_by INTEGER REFERENCES users(id),
    performed_at TIMESTAMPTZ DEFAULT NOW(),
    source_id INTEGER REFERENCES sources(id),
    action enum_log_action NOT NULL,
    details JSONB
);

-- Indexes for performance

-- Foreign key indexes
CREATE INDEX idx_sources_channel_id ON sources(channel_id);
CREATE INDEX idx_sources_status ON sources(status);
CREATE INDEX idx_channels_status ON channels(status);


-- Logs: composite indexes
CREATE INDEX idx_users_logs_user_action ON users_logs(user_id, action);
CREATE INDEX idx_users_logs_performed_by ON users_logs(performed_by);
CREATE INDEX idx_users_logs_performed_at ON users_logs(performed_at);

CREATE INDEX idx_channels_logs_channel_action ON channels_logs(channel_id, action);
CREATE INDEX idx_channels_logs_performed_by ON channels_logs(performed_by);
CREATE INDEX idx_channels_logs_performed_at ON channels_logs(performed_at);

CREATE INDEX idx_sources_logs_source_action ON sources_logs(source_id, action);
CREATE INDEX idx_sources_logs_performed_by ON sources_logs(performed_by);
CREATE INDEX idx_sources_logs_performed_at ON sources_logs(performed_at);