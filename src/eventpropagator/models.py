from pydantic import BaseModel

class Config(BaseModel):
    interval_seconds: float
    api_endpoint: str
    events_file: str