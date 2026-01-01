#In this file, we define the JobExecution model for tracking the execution details of jobs in the job scheduler application and define the database schema for job executions.




import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base
from app.models.enums import ExecutionStatus


class JobExecution(Base):
    __tablename__ = "job_executions"

    __table_args__ = (
        UniqueConstraint("job_id", "attempt_number", name="uq_job_attempt"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    job_id = Column(
        UUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False
    )

    attempt_number = Column(Integer, nullable=False)

    started_at = Column(
        DateTime(timezone=True),
        nullable=False
    )
    finished_at = Column(DateTime(timezone=True), nullable=True)

    status = Column(Enum(ExecutionStatus), nullable=False)
    error_message = Column(String, nullable=True)

    job = relationship("Job", back_populates="executions")










