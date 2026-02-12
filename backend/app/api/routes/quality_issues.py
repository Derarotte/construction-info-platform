from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entities import QualityIssue, QualityIssueEvent
from app.models.enums import QualityIssueStatus
from app.schemas.quality import (
    QualityIssueCreate,
    QualityIssueEventOut,
    QualityIssueOut,
    QualityIssueTransition,
    QualityIssueUpdate,
)

router = APIRouter()

TRANSITIONS: dict[QualityIssueStatus, set[QualityIssueStatus]] = {
    QualityIssueStatus.reported: {QualityIssueStatus.rectifying, QualityIssueStatus.rejected},
    QualityIssueStatus.rectifying: {QualityIssueStatus.pending_review, QualityIssueStatus.rejected},
    QualityIssueStatus.pending_review: {
        QualityIssueStatus.closed,
        QualityIssueStatus.rectifying,
        QualityIssueStatus.rejected,
    },
    QualityIssueStatus.closed: set(),
    QualityIssueStatus.rejected: {QualityIssueStatus.rectifying},
}


def to_out(row: QualityIssue) -> QualityIssueOut:
    return QualityIssueOut(
        id=row.id,
        project_id=row.project_id,
        section_id=row.section_id,
        work_area_id=row.work_area_id,
        issue_code=row.issue_code,
        title=row.title,
        description=row.description,
        level=row.level.value,
        status=row.status.value,
        owner_name=row.owner_name,
        reporter_name=row.reporter_name,
        reported_at=row.reported_at,
        due_at=row.due_at,
        closed_at=row.closed_at,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def event_out(row: QualityIssueEvent) -> QualityIssueEventOut:
    return QualityIssueEventOut(
        id=row.id,
        issue_id=row.issue_id,
        from_status=row.from_status.value if row.from_status else None,
        to_status=row.to_status.value,
        action_by=row.action_by,
        action_note=row.action_note,
        action_at=row.action_at,
    )


@router.get("/quality-issues", response_model=list[QualityIssueOut])
def list_quality_issues(
    project_id: str | None = Query(default=None),
    status: QualityIssueStatus | None = Query(default=None),
    db: Session = Depends(get_db),
):
    stmt = select(QualityIssue).order_by(QualityIssue.created_at.desc())
    if project_id:
        stmt = stmt.where(QualityIssue.project_id == project_id)
    if status:
        stmt = stmt.where(QualityIssue.status == status)
    rows = db.scalars(stmt.limit(500)).all()
    return [to_out(row) for row in rows]


@router.get("/quality-issues/{issue_id}", response_model=QualityIssueOut)
def get_quality_issue(issue_id: str, db: Session = Depends(get_db)):
    row = db.get(QualityIssue, issue_id)
    if not row:
        raise HTTPException(status_code=404, detail="quality issue not found")
    return to_out(row)


@router.post("/quality-issues", response_model=QualityIssueOut)
def create_quality_issue(payload: QualityIssueCreate, db: Session = Depends(get_db)):
    now = datetime.utcnow()
    row = QualityIssue(
        project_id=payload.project_id,
        section_id=payload.section_id,
        work_area_id=payload.work_area_id,
        issue_code=payload.issue_code,
        title=payload.title,
        description=payload.description,
        level=payload.level,
        status=QualityIssueStatus.reported,
        owner_name=payload.owner_name,
        reporter_name=payload.reporter_name,
        reported_at=now,
        due_at=payload.due_at,
        created_at=now,
        updated_at=now,
    )
    db.add(row)
    db.flush()
    db.add(
        QualityIssueEvent(
            issue_id=row.id,
            from_status=None,
            to_status=QualityIssueStatus.reported,
            action_by=payload.reporter_name or "system",
            action_note="issue reported",
            action_at=now,
        )
    )
    db.commit()
    db.refresh(row)
    return to_out(row)


@router.patch("/quality-issues/{issue_id}", response_model=QualityIssueOut)
def update_quality_issue(issue_id: str, payload: QualityIssueUpdate, db: Session = Depends(get_db)):
    row = db.get(QualityIssue, issue_id)
    if not row:
        raise HTTPException(status_code=404, detail="quality issue not found")

    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(row, k, v)
    row.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(row)
    return to_out(row)


@router.post("/quality-issues/{issue_id}/transition", response_model=QualityIssueOut)
def transition_quality_issue(issue_id: str, payload: QualityIssueTransition, db: Session = Depends(get_db)):
    row = db.get(QualityIssue, issue_id)
    if not row:
        raise HTTPException(status_code=404, detail="quality issue not found")

    allowed = TRANSITIONS.get(row.status, set())
    if payload.to_status not in allowed:
        raise HTTPException(status_code=400, detail=f"invalid transition: {row.status.value} -> {payload.to_status.value}")

    now = datetime.utcnow()
    from_status = row.status
    row.status = payload.to_status
    row.updated_at = now
    row.closed_at = now if payload.to_status == QualityIssueStatus.closed else None
    db.add(
        QualityIssueEvent(
            issue_id=row.id,
            from_status=from_status,
            to_status=payload.to_status,
            action_by=payload.actor,
            action_note=payload.note,
            action_at=now,
        )
    )
    db.commit()
    db.refresh(row)
    return to_out(row)


@router.get("/quality-issues/{issue_id}/events", response_model=list[QualityIssueEventOut])
def list_quality_events(issue_id: str, db: Session = Depends(get_db)):
    rows = db.scalars(
        select(QualityIssueEvent)
        .where(QualityIssueEvent.issue_id == issue_id)
        .order_by(QualityIssueEvent.action_at.desc())
    ).all()
    return [event_out(row) for row in rows]
