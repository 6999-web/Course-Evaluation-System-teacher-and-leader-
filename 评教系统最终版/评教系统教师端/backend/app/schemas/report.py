from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ReportItem(BaseModel):
    """报告项"""
    id: int
    report_name: str
    report_type: str
    generate_date: datetime
    status: str
    file_path: Optional[str] = None
    generated_by: str

    class Config:
        from_attributes = True
