# In this file, we start the worker process for the job scheduler application, which is responsible for executing scheduled jobs.

from app.worker.scheduler import start_worker

print("WORKER PROCESS STARTED")
start_worker()
