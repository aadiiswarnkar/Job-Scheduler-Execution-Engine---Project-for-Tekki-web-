# In this file, we define the job execution logic for the job scheduler application, handling job execution, retries, and status updates and implement the execute_job function. along with necessary imports. 

import random
import time
from datetime import datetime, timezone, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.job_execution import JobExecution
from app.models.enums import (
    ExecutionStatus,
    JobStatus,
    ScheduleType
)


def execute_job(db: Session, job):
    """
    Executes a job safely with retry handling.
    - ONE_TIME jobs: retry until max_retries, then FAILED
    - INTERVAL jobs: NEVER permanently fail, always reschedule
    """

    #  Extra safety: refresh job state
    db.refresh(job)

    #  Calculate next attempt number atomically
    attempt_number = (
        db.query(JobExecution)
        .filter(JobExecution.job_id == job.id)
        .count()
        + 1
    )

    #  Create execution record (initially FAILED, updated later)
    execution = JobExecution(
        job_id=job.id,
        attempt_number=attempt_number,
        started_at=datetime.now(timezone.utc),
        status=ExecutionStatus.FAILED
    )

    db.add(execution)
    db.flush()  # execution.id generated, but no commit yet

    try:
        # Simulate execution time
        time.sleep(random.randint(1, 3))

        # 💥 30% random failure
        if random.random() < 0.3:
            raise Exception("Simulated random failure")

        #  SUCCESS
        execution.status = ExecutionStatus.SUCCESS

        if job.schedule_type == ScheduleType.INTERVAL:
            #  INTERVAL job → always reschedule
            job.run_at = func.now() + timedelta(seconds=job.interval_seconds)
            job.status = JobStatus.SCHEDULED
        else:
            #  ONE_TIME job completed
            job.status = JobStatus.COMPLETED

    except Exception as e:
        execution.error_message = str(e)

        if job.schedule_type == ScheduleType.INTERVAL:
            # INTERVAL job NEVER permanently fails
            job.run_at = func.now() + timedelta(seconds=job.interval_seconds)
            job.status = JobStatus.SCHEDULED

        else:
            #  ONE_TIME retry logic
            if attempt_number <= job.max_retries:
                job.status = JobStatus.SCHEDULED
            else:
                job.status = JobStatus.FAILED

    finally:
        execution.finished_at = datetime.now(timezone.utc)
        db.commit()


