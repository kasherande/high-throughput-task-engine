import enum
from sqlalchemy import Column, String, DateTime, Enum, Text
from datetime import datetime
from app.core.database import Base

class TaskStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class TaskLog(Base):
    __tablename__ = "task_logs"

    task_id = Column(String(255), primary_key=True, index=True)
    payload = Column(Text, nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, index=True)
    result = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)