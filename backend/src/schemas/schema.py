from sqlalchemy import Column, Integer, Boolean, ForeignKey, Enum, Text, LargeBinary, TIMESTAMP, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import CITEXT, JSONB
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

# ENUM Types
class UserRole(enum.Enum):
    admin = 'admin'
    editor = 'editor'
    viewer = 'viewer'

class RunningStatus(enum.Enum):
    active = 'active'
    pending = 'pending'
    inactive = 'inactive'

class ModelTask(enum.Enum):
    detection = 'detection'
    segmentation = 'segmentation'
    estimation = 'estimation'

class ModelWeight(enum.Enum):
    nano = 'nano'
    small = 'small'
    medium = 'medium'
    large = 'large'
    x_large = 'x-large'

class LogAction(enum.Enum):
    create = 'create'
    update = 'update'
    delete = 'delete'
    

# Table: users
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    email = Column(CITEXT, unique=True, nullable=False)
    password = Column(LargeBinary, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.editor)

# Table: channels
class Channel(Base):
    __tablename__ = 'channels'

    id = Column(Integer, primary_key=True)
    name = Column(CITEXT, unique=True, nullable=False)
    status = Column(Enum(RunningStatus), default=RunningStatus.active)

    confidence = Column(Integer, nullable=False)
    overlapping = Column(Integer, nullable=False)
    realtime = Column(Boolean, nullable=False)
    augmentation = Column(Boolean, nullable=False)
    tracking = Column(Boolean, nullable=False)
    reid = Column(Boolean, nullable=False)

    plotting_config = Column(JSONB, nullable=False, default=dict)

# Table: sources
class Source(Base):
    __tablename__ = 'sources'

    id = Column(Integer, primary_key=True)
    channel_id = Column(Integer, ForeignKey('channels.id'))
    name = Column(CITEXT, nullable=False)
    url = Column(Text, nullable=False)
    status = Column(Enum(RunningStatus), default=RunningStatus.active)

    __table_args__ = (
        UniqueConstraint('channel_id', 'name', name='unique_source_name_per_channel'),
    )

# Table: models
class Model(Base):
    __tablename__ = 'models'

    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True, nullable=False)
    task = Column(Enum(ModelTask), nullable=False)
    weight = Column(Enum(ModelWeight), nullable=False)
    classes = Column(JSONB)

# Table: channels_users
class ChannelUser(Base):
    __tablename__ = 'channels_users'

    channel_id = Column(Integer, ForeignKey('channels.id', ondelete='CASCADE'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)

# Table: channels_models
class ChannelModel(Base):
    __tablename__ = 'channels_models'

    channel_id = Column(Integer, ForeignKey('channels.id', ondelete='CASCADE'), primary_key=True)
    model_id = Column(Integer, ForeignKey('models.id', ondelete='CASCADE'), primary_key=True)

# Table: users_logs
class UserLog(Base):
    __tablename__ = 'users_logs'

    id = Column(Integer, primary_key=True)
    performed_by = Column(Integer, ForeignKey('users.id'))
    performed_at = Column(TIMESTAMP(timezone=True), default='now()')
    user_id = Column(Integer, ForeignKey('users.id'))
    action = Column(Enum(LogAction), nullable=False)
    details = Column(JSONB)

# Table: channels_logs
class ChannelLog(Base):
    __tablename__ = 'channels_logs'

    id = Column(Integer, primary_key=True)
    performed_by = Column(Integer, ForeignKey('users.id'))
    performed_at = Column(TIMESTAMP(timezone=True), default='now()')
    channel_id = Column(Integer, ForeignKey('channels.id'))
    action = Column(Enum(LogAction), nullable=False)
    details = Column(JSONB)

# Table: sources_logs
class SourceLog(Base):
    __tablename__ = 'sources_logs'

    id = Column(Integer, primary_key=True)
    performed_by = Column(Integer, ForeignKey('users.id'))
    performed_at = Column(TIMESTAMP(timezone=True), default='now()')
    source_id = Column(Integer, ForeignKey('sources.id'))
    action = Column(Enum(LogAction), nullable=False)
    details = Column(JSONB)

# Indexes (you may want to apply them manually via Alembic or separate migrations)
Index('idx_sources_channel_id', Source.channel_id)
Index('idx_sources_status', Source.status)
Index('idx_channels_status', Channel.status)

Index('idx_users_logs_user_action', UserLog.user_id, UserLog.action)
Index('idx_users_logs_performed_by', UserLog.performed_by)
Index('idx_users_logs_performed_at', UserLog.performed_at)

Index('idx_channels_logs_channel_action', ChannelLog.channel_id, ChannelLog.action)
Index('idx_channels_logs_performed_by', ChannelLog.performed_by)
Index('idx_channels_logs_performed_at', ChannelLog.performed_at)

Index('idx_sources_logs_source_action', SourceLog.source_id, SourceLog.action)
Index('idx_sources_logs_performed_by', SourceLog.performed_by)
Index('idx_sources_logs_performed_at', SourceLog.performed_at)
