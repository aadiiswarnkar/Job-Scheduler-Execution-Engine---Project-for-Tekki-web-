#In this file, we define the JobRepository class for managing job-related database operations in the job scheduler application and implement methods for fetching and recovering jobs.



from datetime import timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.sql import select

from app.models.job import Job
from app.models.job_execution import JobExecution
from app.models.enums import JobStatus


def fetch_and_lock_due_job(db: Session):
    job = (
        db.execute(
            select(Job)
            .where(
                Job.status == JobStatus.SCHEDULED,
                Job.run_at <= func.now()
            )
            .order_by(Job.run_at.asc())
            .with_for_update(skip_locked=True)
        )
        .scalars()
        .first()
    )

    if not job:
        return None

    job.status = JobStatus.RUNNING
    db.commit()
    return job


def recover_stuck_jobs(db: Session, timeout_minutes: int = 5):
    """
    Recover jobs stuck in RUNNING state due to worker crash.
    A job is considered stuck if:
    - status = RUNNING
    - it has an unfinished JobExecution
    - execution started before timeout
    """

    cutoff_time = func.now() - timedelta(minutes=timeout_minutes)

    stuck_jobs = (
        db.query(Job)
        .join(JobExecution, JobExecution.job_id == Job.id)
        .filter(
            Job.status == JobStatus.RUNNING,
            JobExecution.finished_at.is_(None),
            JobExecution.started_at < cutoff_time
        )
        .all()
    )

    recovered_ids = []

    for job in stuck_jobs:
        job.status = JobStatus.SCHEDULED
        recovered_ids.append(str(job.id))

    db.commit()
    return recovered_ids


