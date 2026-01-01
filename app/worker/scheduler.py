# In this file, we define the main worker loop for the job scheduler application, which continuously fetches and executes due jobs while handling crash recovery. and implement the start_worker function along with necessary imports. and crash recovery logic. along with necessary imports.

from app.db.session import SessionLocal, init_db
from app.models.job_repository import (
    fetch_and_lock_due_job,
    recover_stuck_jobs
)
from app.servies.job_executor import execute_job
import time


def start_worker():
    #  Ensure DB tables exist (CRITICAL for Docker)
    init_db()

    # Crash recovery on startup
    db = SessionLocal()
    try:
        recovered = recover_stuck_jobs(db, timeout_minutes=1)
        if recovered:
            print(f"♻️ Recovered {len(recovered)} stuck jobs")
    finally:
        db.close()

    #  Main worker loop
    while True:
        db = SessionLocal()
        try:
            job = fetch_and_lock_due_job(db)

            if not job:
                time.sleep(2)
                continue

            execute_job(db, job)

        finally:
            db.close()


