from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import time
import threading

from backend.database import engine, get_db
from backend import models

app = FastAPI(title="GPU Service Demo")

# 🔹 CORS (خیلی مهم برای اتصال فرانت)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ساخت جدول‌ها
models.Base.metadata.create_all(bind=engine)

# ---------------- USERS ----------------

@app.post("/register")
def register(username: str, password: str, db: Session = Depends(get_db)):
    # اگر یوزر admin باشه → نقش admin
    role = "admin" if username == "admin" else "user"

    user = models.User(
        username=username,
        password=password,
        role=role
    )
    db.add(user)
    db.commit()
    return {"message": "user created", "role": role}


@app.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = (
        db.query(models.User)
        .filter_by(username=username, password=password)
        .first()
    )
    if not user:
        return {"error": "invalid credentials"}

    return {
        "user_id": user.id,
        "role": user.role
    }


# ---------------- JOBS ----------------

@app.post("/jobs")
def create_job(user_id: int, command: str, db: Session = Depends(get_db)):
    job = models.Job(
        user_id=user_id,
        command=command,
        status="PENDING"
    )
    db.add(job)
    db.commit()
    return {
        "job_id": job.id,
        "status": job.status
    }


@app.get("/jobs")
def list_jobs(db: Session = Depends(get_db)):
    return db.query(models.Job).all()


# ---------------- ADMIN ----------------

@app.post("/admin/approve")
def approve_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(models.Job).get(job_id)
    job.status = "APPROVED"
    db.commit()
    return {"status": "APPROVED"}


def simulate_gpu(job_id: int):
    db = next(get_db())
    job = db.query(models.Job).get(job_id)

    job.status = "RUNNING"
    db.commit()

    time.sleep(5)  # شبیه‌سازی GPU

    job.status = "COMPLETED"
    db.commit()


@app.post("/admin/run")
def run_job(job_id: int):
    threading.Thread(target=simulate_gpu, args=(job_id,)).start()
    return {"status": "RUNNING"}
