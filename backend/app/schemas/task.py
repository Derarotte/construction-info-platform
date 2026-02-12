from datetime import date
from pydantic import BaseModel, Field

from app.models.enums import TaskStatus


class TaskCreate(BaseModel):
    project_id: str
    parent_task_id: str | None = None
    wbs_code: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=255)
    status: TaskStatus = TaskStatus.not_started
    planned_start: date | None = None
    planned_end: date | None = None
    actual_start: date | None = None
    actual_end: date | None = None
    planned_days: int | None = None
    actual_days: int | None = None
    progress_percent: float = 0
    predecessor_task_ids: list[str] = []


class TaskUpdate(BaseModel):
    parent_task_id: str | None = None
    wbs_code: str | None = None
    name: str | None = None
    status: TaskStatus | None = None
    planned_start: date | None = None
    planned_end: date | None = None
    actual_start: date | None = None
    actual_end: date | None = None
    planned_days: int | None = None
    actual_days: int | None = None
    progress_percent: float | None = None
    predecessor_task_ids: list[str] | None = None


class TaskOut(BaseModel):
    id: str
    project_id: str
    parent_task_id: str | None
    wbs_code: str
    name: str
    status: str
    planned_start: date | None
    planned_end: date | None
    actual_start: date | None
    actual_end: date | None
    planned_days: int | None
    actual_days: int | None
    progress_percent: float
    predecessor_task_ids: list[str]


class CriticalPathOut(BaseModel):
    cycle: bool
    planned_length: int
    actual_length: int
    planned_path_task_ids: list[str]
    actual_path_task_ids: list[str]
