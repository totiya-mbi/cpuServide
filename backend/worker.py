import time
from backend.database import SessionLocal
from backend.models import Job


def simulate_job(job_id: int):
    db = SessionLocal()
    job = db.query(Job).get(job_id)

    job.status = "RUNNING"
    db.commit()

    time.sleep(job.estimated_hours)

    job.status = "COMPLETED"
    db.commit()
