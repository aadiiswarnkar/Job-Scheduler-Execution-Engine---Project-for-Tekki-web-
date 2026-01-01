# Job Scheduler & Execution Engine (Backend Logic Assignment)

This project implements a **robust Job Scheduler and Execution Engine** focused on
backend correctness, state transitions, retry handling, and safe concurrent execution.

It is designed as a **logic-first system**, not a UI-heavy application.

---

## 🧠 Core Concepts Covered

- One-time and interval-based job scheduling
- Safe job picking with database-level locking
- Retry handling with max retry limits
- Crash recovery for stuck jobs
- Separation of API and worker processes
- Dockerized, reproducible setup

---

## 🏗️ Architecture Overview

The system is split into **three services**:

Flask API -> PostgreSQL -> Worker Process 


### Components

- **API Service**
  - Accepts job creation requests
  - Exposes job status & execution history
  - Swagger/OpenAPI documentation enabled

- **Worker Service**
  - Polls for due jobs
  - Executes jobs safely
  - Handles retries and rescheduling
  - Performs crash recovery on startup

- **PostgreSQL**
  - Source of truth
  - Enforces concurrency guarantees

---

## 📦 Tech Stack

- Python 3.11
- Flask
- SQLAlchemy 2.x
- PostgreSQL
- Docker & Docker Compose
- Flasgger (Swagger UI)

---

---

## 🔄 Job Lifecycle

### ONE_TIME Job

SCHEDULED → RUNNING → COMPLETED


and FAILED (after max retries)

### INTERVAL Job

SCHEDULED → RUNNING → SCHEDULED → RUNNING → ...
(never permanently fails)



---

## 🔁 Retry & Failure Handling

- Each execution attempt is recorded in `job_executions`
- Failed executions retry until `max_retries` is exceeded
- Interval jobs **never permanently fail**
- Random failures are simulated to test robustness

---

## ♻️ Crash Recovery

On worker startup:

- Jobs stuck in `RUNNING` state beyond a timeout
- Are safely reset back to `SCHEDULED`
- Prevents orphaned jobs after crashes

---

## 🚀 Running the Project (Recommended)

### Prerequisites
- Docker
- Docker Compose

### Start all services

docker-compose up --build

This starts:

Flask API → http://localhost:5000

Swagger UI → http://localhost:5000/apidocs

Background worker

PostgreSQL database


API Documentation (Swagger) = http://localhost:5000/apidocs


Environment Variables

Create a .env file (not committed): DATABASE_URL=postgresql://postgres:postgres@postgres:5432/jobs_db


✅ Key Design Decisions

Database locking is used instead of in-memory locks

Worker and API are separate processes

Idempotent execution design

Explicit state transitions

No duplicate execution possible under concurrency

The project prioritizes correctness over features

No Celery / Redis used intentionally

All concurrency guarantees are DB-backed

Code is written to be readable and reviewable


