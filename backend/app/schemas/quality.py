from datetime import datetime
from pydantic import BaseModel, Field

from app.models.enums import QualityIssueStatus, QualityLevel


class QualityIssueCreate(BaseModel):
    project_id: str
    section_id: str | None = None
    work_area_id: str | None = None
    issue_code: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    level: QualityLevel = QualityLevel.medium
    owner_name: str | None = None
    reporter_name: str | None = None
    due_at: datetime | None = None


class QualityIssueUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    level: QualityLevel | None = None
    owner_name: str | None = None
    due_at: datetime | None = None


class QualityIssueTransition(BaseModel):
    to_status: QualityIssueStatus
    note: str = ""
    actor: str = "system"


class QualityIssueOut(BaseModel):
    id: str
    project_id: str
    section_id: str | None
    work_area_id: str | None
    issue_code: str
    title: str
    description: str | None
    level: str
    status: str
    owner_name: str | None
    reporter_name: str | None
    reported_at: datetime
    due_at: datetime | None
    closed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class QualityIssueEventOut(BaseModel):
    id: str
    issue_id: str
    from_status: str | None
    to_status: str
    action_by: str | None
    action_note: str | None
    action_at: datetime
