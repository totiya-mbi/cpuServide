from backend.models import Job, User


class JobService:
    """
    Handles job lifecycle and validation.
    """

    def submit_job(self, user: User, data: dict) -> Job:
        if user.gpu_quota_hours < data["estimated_hours"]:
            raise ValueError("Quota exceeded")

        return Job(
            user_id=user.id,
            **data
        )
