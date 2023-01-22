from pydantic import BaseModel


class BaseUser(BaseModel):
    username: str
    jobs: int = 0
    jobs_complete: int = 0


class BaseJob(BaseModel):
    name: str
    user_id: int
    description: str
    complete: bool = False
