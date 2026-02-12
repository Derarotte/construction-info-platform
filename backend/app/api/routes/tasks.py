from collections import defaultdict, deque
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entities import Task, TaskDependency
from app.models.enums import DependencyType
from app.schemas.task import CriticalPathOut, TaskCreate, TaskOut, TaskUpdate

router = APIRouter()


def serialize_task(task: Task, predecessor_task_ids: list[str]) -> TaskOut:
    return TaskOut(
        id=task.id,
        project_id=task.project_id,
        parent_task_id=task.parent_task_id,
        wbs_code=task.wbs_code,
        name=task.name,
        status=task.status.value,
        planned_start=task.planned_start,
        planned_end=task.planned_end,
        actual_start=task.actual_start,
        actual_end=task.actual_end,
        planned_days=task.planned_days,
        actual_days=task.actual_days,
        progress_percent=float(task.progress_percent),
        predecessor_task_ids=predecessor_task_ids,
    )


def load_dependencies(db: Session, project_id: str) -> dict[str, list[str]]:
    rows = db.scalars(
        select(TaskDependency).where(TaskDependency.project_id == project_id)
    ).all()
    deps: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        deps[row.successor_task_id].append(row.predecessor_task_id)
    return deps


@router.get("/tasks", response_model=list[TaskOut])
def list_tasks(project_id: str | None = Query(default=None), db: Session = Depends(get_db)):
    stmt = select(Task).order_by(Task.created_at.desc())
    if project_id:
        stmt = stmt.where(Task.project_id == project_id)
    rows = db.scalars(stmt.limit(1000)).all()
    project_ids = {row.project_id for row in rows}
    dep_map: dict[str, list[str]] = {}
    for pid in project_ids:
        dep_map.update(load_dependencies(db, pid))
    return [serialize_task(row, dep_map.get(row.id, [])) for row in rows]


@router.post("/tasks", response_model=TaskOut)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    now = datetime.utcnow()
    row = Task(
        project_id=payload.project_id,
        parent_task_id=payload.parent_task_id,
        wbs_code=payload.wbs_code,
        name=payload.name,
        status=payload.status,
        planned_start=payload.planned_start,
        planned_end=payload.planned_end,
        actual_start=payload.actual_start,
        actual_end=payload.actual_end,
        planned_days=payload.planned_days,
        actual_days=payload.actual_days,
        progress_percent=payload.progress_percent,
        created_at=now,
        updated_at=now,
    )
    db.add(row)
    db.flush()
    for predecessor in payload.predecessor_task_ids:
        db.add(
            TaskDependency(
                project_id=payload.project_id,
                predecessor_task_id=predecessor,
                successor_task_id=row.id,
                dependency_type=DependencyType.fs,
                lag_days=0,
                created_at=now,
            )
        )
    db.commit()
    db.refresh(row)
    return serialize_task(row, payload.predecessor_task_ids)


@router.patch("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: str, payload: TaskUpdate, db: Session = Depends(get_db)):
    row = db.get(Task, task_id)
    if not row:
        raise HTTPException(status_code=404, detail="task not found")

    data = payload.model_dump(exclude_unset=True, exclude={"predecessor_task_ids"})
    for k, v in data.items():
        setattr(row, k, v)
    row.updated_at = datetime.utcnow()

    predecessor_task_ids = payload.predecessor_task_ids
    if predecessor_task_ids is not None:
        db.execute(
            delete(TaskDependency).where(
                TaskDependency.project_id == row.project_id,
                TaskDependency.successor_task_id == row.id,
            )
        )
        for predecessor in predecessor_task_ids:
            db.add(
                TaskDependency(
                    project_id=row.project_id,
                    predecessor_task_id=predecessor,
                    successor_task_id=row.id,
                    dependency_type=DependencyType.fs,
                    lag_days=0,
                    created_at=datetime.utcnow(),
                )
            )

    db.commit()
    db.refresh(row)
    final_predecessors = predecessor_task_ids if predecessor_task_ids is not None else load_dependencies(db, row.project_id).get(row.id, [])
    return serialize_task(row, final_predecessors)


@router.delete("/tasks/{task_id}")
def delete_task(task_id: str, db: Session = Depends(get_db)):
    row = db.get(Task, task_id)
    if not row:
        raise HTTPException(status_code=404, detail="task not found")
    db.delete(row)
    db.commit()
    return {"ok": True}


def compute_critical_path(tasks: list[Task], dependencies: list[TaskDependency], use_actual: bool) -> tuple[bool, int, list[str]]:
    task_map = {t.id: t for t in tasks}
    indegree: dict[str, int] = {t.id: 0 for t in tasks}
    next_map: dict[str, list[str]] = defaultdict(list)
    pred_map: dict[str, list[str]] = defaultdict(list)

    for dep in dependencies:
        if dep.predecessor_task_id not in task_map or dep.successor_task_id not in task_map:
            continue
        next_map[dep.predecessor_task_id].append(dep.successor_task_id)
        pred_map[dep.successor_task_id].append(dep.predecessor_task_id)
        indegree[dep.successor_task_id] += 1

    q = deque([k for k, v in indegree.items() if v == 0])
    order: list[str] = []
    while q:
        cur = q.popleft()
        order.append(cur)
        for n in next_map.get(cur, []):
            indegree[n] -= 1
            if indegree[n] == 0:
                q.append(n)

    if len(order) != len(tasks):
        return True, 0, []

    dist: dict[str, int] = {}
    prev: dict[str, str | None] = {}
    for node in order:
        preds = pred_map.get(node, [])
        best_prev = None
        best = 0
        for p in preds:
            if dist.get(p, 0) > best:
                best = dist.get(p, 0)
                best_prev = p
        days = task_map[node].actual_days if use_actual else task_map[node].planned_days
        dist[node] = best + max(days or 0, 0)
        prev[node] = best_prev

    end_id = max(order, key=lambda i: dist.get(i, 0))
    total = dist.get(end_id, 0)
    path: list[str] = []
    cur: str | None = end_id
    while cur:
        path.insert(0, cur)
        cur = prev.get(cur)
    return False, total, path


@router.get("/tasks/critical-path", response_model=CriticalPathOut)
def critical_path(project_id: str = Query(...), db: Session = Depends(get_db)):
    tasks = db.scalars(select(Task).where(Task.project_id == project_id)).all()
    deps = db.scalars(select(TaskDependency).where(TaskDependency.project_id == project_id)).all()
    cycle, planned_len, planned_path = compute_critical_path(tasks, deps, use_actual=False)
    if cycle:
        return CriticalPathOut(
            cycle=True,
            planned_length=0,
            actual_length=0,
            planned_path_task_ids=[],
            actual_path_task_ids=[],
        )
    _, actual_len, actual_path = compute_critical_path(tasks, deps, use_actual=True)
    return CriticalPathOut(
        cycle=False,
        planned_length=planned_len,
        actual_length=actual_len,
        planned_path_task_ids=planned_path,
        actual_path_task_ids=actual_path,
    )
