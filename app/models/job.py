# In this file, we define the Job model for the job scheduler application, including its attributes and relationships to other models and define the database schema for jobs and their properties.

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Integer, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base
from app.models.enums import JobStatus, ScheduleType


class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    payload = Column(JSON, nullable=True)

    schedule_type = Column(Enum(ScheduleType), nullable=False)
    run_at = Column(DateTime(timezone=True), nullable=False)
    interval_seconds = Column(Integer, nullable=True)

    max_retries = Column(Integer, nullable=False, default=0)

    status = Column(
        Enum(JobStatus),
        nullable=False,
        default=JobStatus.SCHEDULED
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    executions = relationship(
        "JobExecution",
        back_populates="job",
        cascade="all, delete-orphan"
    )












