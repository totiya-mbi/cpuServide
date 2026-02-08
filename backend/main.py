from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import engine, get_db
from backend import models, schemas, auth

from backend.schemas import JobCreate
from backend.auth import get_current_user
from backend.auth import require_admin

import time
from fastapi import HTTPException
from fastapi.openapi.utils import get_openapi


app = FastAPI(title="GPU as a Service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # برای دمو و پروژه دانشجویی
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"status": "ok"}


# -------- AUTH --------

@app.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter_by(username=user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    new_user = models.User(
        username=user.username,
        password_hash=auth.hash_password(user.password),
        role="admin" if user.username == "admin" else "user"
    )
    db.add(new_user)
    db.commit()

    return {"message": "user created"}


@app.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter_by(username=user.username).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not auth.verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = auth.create_access_token({
        "sub": db_user.username,
        "role": db_user.role,
        "user_id": db_user.id
    })

    return {"access_token": token, "token_type": "bearer"}


@app.post("/jobs")
def create_job(
    job: JobCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    new_job = models.Job(
        user_id=user["user_id"],
        command=job.command,
        status="PENDING"
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return {
        "job_id": new_job.id,
        "status": new_job.status
    }
@app.get("/jobs")
def get_jobs(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user["role"] == "admin":
        return db.query(models.Job).all()
    else:
        return db.query(models.Job).filter(
            models.Job.user_id == user["user_id"]
        ).all()
        
@app.post("/admin/jobs/{job_id}/approve")
def approve_job(
    job_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    job = db.query(models.Job).filter_by(id=job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != "PENDING":
        raise HTTPException(status_code=400, detail="Job not in PENDING state")

    job.status = "APPROVED"
    db.commit()

    return {
        "job_id": job.id,
        "new_status": job.status
    }
    
@app.post("/admin/jobs/{job_id}/run")
def run_job(
    job_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    job = db.query(models.Job).filter_by(id=job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != "APPROVED":
        raise HTTPException(
            status_code=400,
            detail="Job must be APPROVED before running"
        )

    # شبیه‌سازی اجرا
    job.status = "RUNNING"
    db.commit()

    time.sleep(3)  # شبیه‌سازی زمان اجرا (۳ ثانیه)

    job.status = "COMPLETED"
    db.commit()

    return {
        "job_id": job.id,
        "final_status": job.status
    }
 
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
    )

    # مطمئن شو components وجود دارد
    openapi_schema.setdefault("components", {})
    openapi_schema["components"].setdefault("securitySchemes", {})

    openapi_schema["components"]["securitySchemes"]["BearerAuth"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    }

    # امنیت پیش‌فرض برای همه endpointها
    openapi_schema["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
