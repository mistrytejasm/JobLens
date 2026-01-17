from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class JobData(BaseModel):
    """
    Data model representing scraped job information.
    """
    title: str
    company: str
    location: Optional[str] = None
    date_posted: Optional[str] = None
    applicants: Optional[str] = None
    description_markdown: str
    job_url: str
    scraped_at: datetime = datetime.now()
