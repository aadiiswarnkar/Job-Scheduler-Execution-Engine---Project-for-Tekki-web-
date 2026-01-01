#In this file, we define the controller for managing job-related endpoints in the job scheduler application and implement CRUD operations for jobs.



from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
from flasgger import swag_from

from app.db.session import SessionLocal
from app.models.job import Job
from app.models.job_execution import JobExecution
from app.models.enums import JobStatus, ScheduleType

jobs_bp = Blueprint("jobs", __name__, url_prefix="/jobs")


# CREATE JOB (POST /jobs)

@jobs_bp.route("", methods=["POST"])
@swag_from({
    "consumes": ["application/json"],
    "tags": ["Jobs"],
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "required": ["name", "schedule_type", "run_at"],
                "properties": {
                    "name": {
                        "type": "string",
                        "example": "sample-job"
                    },
                    "schedule_type": {
                        "type": "string",
                        "enum": ["ONE_TIME", "INTERVAL"],
                        "example": "ONE_TIME"
                    },
                    "run_at": {
                        "type": "string",
                        "format": "date-time",
                        "example": "2026-01-01T10:30:00+00:00"
                    },
                    "interval_seconds": {
                        "type": "integer",
                        "example": 10
                    },
                    "max_retries": {
                        "type": "integer",
                        "example": 2
                    },
                    "payload": {
                        "type": "object",
                        "example": {"task": "send-email"}
                    }
                }
            }
        }
    ],
    "responses": {
        201: {
            "description": "Job created successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"}
                }
            }
        },
        400: {"description": "Validation error"}
    }
})
def create_job():
    data = request.get_json()
    db = SessionLocal()

    try:
        if not data:
            return jsonify({"error": "Request body required"}), 400

        name = data.get("name")
        schedule_type = data.get("schedule_type")
        run_at = data.get("run_at")
        interval_seconds = data.get("interval_seconds")
        max_retries = data.get("max_retries", 0)
        payload = data.get("payload")

        if not name or not schedule_type or not run_at:
            return jsonify({"error": "Missing required fields"}), 400

        try:
            schedule_type = ScheduleType[schedule_type.upper()]
        except KeyError:
            return jsonify({"error": "Invalid schedule_type"}), 400

        try:
            run_at = datetime.fromisoformat(run_at).astimezone(timezone.utc)
        except Exception:
            return jsonify({"error": "Invalid run_at format"}), 400

        if run_at <= datetime.now(timezone.utc):
            return jsonify({"error": "run_at must be in the future"}), 400

        if schedule_type == ScheduleType.INTERVAL:
            if not interval_seconds or interval_seconds <= 0:
                return jsonify({"error": "interval_seconds required for INTERVAL jobs"}), 400

        job = Job(
            name=name,
            payload=payload,
            schedule_type=schedule_type,
            run_at=run_at,
            interval_seconds=interval_seconds,
            max_retries=max_retries,
            status=JobStatus.SCHEDULED
        )

        db.add(job)
        db.commit()

        return jsonify({"id": str(job.id)}), 201

    finally:
        db.close()



# LIST JOBS (GET /jobs)

@jobs_bp.route("", methods=["GET"])
@swag_from({
    "tags": ["Jobs"],
    "parameters": [
        {
            "name": "status",
            "in": "query",
            "type": "string",
            "enum": ["SCHEDULED", "RUNNING", "COMPLETED", "FAILED"],
            "required": False
        },
        {
            "name": "schedule_type",
            "in": "query",
            "type": "string",
            "enum": ["ONE_TIME", "INTERVAL"],
            "required": False
        }
    ],
    "responses": {
        200: {
            "description": "List of jobs",
            "schema": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "name": {"type": "string"},
                        "status": {"type": "string"},
                        "schedule_type": {"type": "string"},
                        "run_at": {"type": "string"}
                    }
                }
            }
        }
    }
})
def list_jobs():
    db = SessionLocal()
    try:
        jobs = db.query(Job).all()
        return jsonify([
            {
                "id": str(j.id),
                "name": j.name,
                "status": j.status.value,
                "schedule_type": j.schedule_type.value,
                "run_at": j.run_at.isoformat()
            } for j in jobs
        ])
    finally:
        db.close()



# JOB DETAILS (GET /jobs/{job_id})

@jobs_bp.route("/<job_id>", methods=["GET"])
@swag_from({
    "tags": ["Jobs"],
    "parameters": [
        {
            "name": "job_id",
            "in": "path",
            "type": "string",
            "required": True
        }
    ],
    "responses": {
        200: {
            "description": "Job details with execution history",
            "schema": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "status": {"type": "string"},
                    "executions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "attempt": {"type": "integer"},
                                "status": {"type": "string"},
                                "error": {"type": "string"}
                            }
                        }
                    }
                }
            }
        },
        404: {"description": "Job not found"}
    }
})
def get_job(job_id):
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return jsonify({"error": "Job not found"}), 404

        executions = (
            db.query(JobExecution)
            .filter(JobExecution.job_id == job.id)
            .order_by(JobExecution.attempt_number.asc())
            .all()
        )

        return jsonify({
            "id": str(job.id),
            "name": job.name,
            "status": job.status.value,
            "executions": [
                {
                    "attempt": e.attempt_number,
                    "status": e.status.value,
                    "error": e.error_message
                } for e in executions
            ]
        })
    finally:
        db.close()


