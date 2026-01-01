# In this file, we define enumerations for job statuses, schedule types, and execution statuses used in the job scheduler application and define enum classes for these types.

import enum

class JobStatus(enum.Enum):
    SCHEDULED = "SCHEDULED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class ScheduleType(enum.Enum):
    ONE_TIME = "ONE_TIME"
    INTERVAL = "INTERVAL"

class ExecutionStatus(enum.Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
