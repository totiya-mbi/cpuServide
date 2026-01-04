from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String, default="user")
    gpu_quota_hours = Column(Integer, default=10)


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    gpu_type = Column(String)
    gpu_count = Column(Integer)
    estimated_hours = Column(Integer)
    command = Column(String)
    is_sensitive = Column(Boolean, default=False)
    status = Column(String, default="PENDING")
