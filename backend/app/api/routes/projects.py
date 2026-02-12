from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entities import Project

router = APIRouter()


@router.get("/projects")
def list_projects(db: Session = Depends(get_db)):
    rows = db.scalars(select(Project).order_by(Project.created_at.desc()).limit(200)).all()
    return [
        {
            "id": row.id,
            "name": row.name,
            "code": row.code,
            "status": row.status.value,
            "location": row.location_text,
            "startDate": row.start_date.isoformat() if row.start_date else None,
            "endDate": row.end_date.isoformat() if row.end_date else None,
        }
        for row in rows
    ]
