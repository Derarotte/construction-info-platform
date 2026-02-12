from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.projects import router as project_router
from app.api.routes.quality_issues import router as quality_router
from app.api.routes.tasks import router as task_router
from app.core.config import settings


app = FastAPI(title=settings.app_name)
app.include_router(health_router, prefix="/api")
app.include_router(project_router, prefix="/api")
app.include_router(quality_router, prefix="/api")
app.include_router(task_router, prefix="/api")
