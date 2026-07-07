#THIS IS JUST DEMO DATA FOR INITIAL SCAFFOLDING TO ENSURE BACKEND CONNECTS TO DB
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID, uuid4


class Project(BaseModel):
    id: UUID = uuid4()
    name: str
    created_at: datetime = datetime.utcnow()