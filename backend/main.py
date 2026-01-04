from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import engine, get_db
from backend import models, schemas, auth

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

