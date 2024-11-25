from schemas.schemas import Input

from fastapi import APIRouter
from fastapi.responses import JSONResponse


from celery_tools.celery_tasks.tasks import task_1, task_2
from celery_tools.config.celery_utils import get_task_info
from typing import Any

router = APIRouter(
    prefix="/test", tags=["test"], responses={404: {"description": "Not found"}}
)


@router.post("/")
async def task(input_: Input) -> JSONResponse:
    if input_.task == "task_1":
        response = task_1.apply_async(args=[input_])
    elif input_.task == "task_2":
        response = task_2.apply_async(args=[input_])
    return JSONResponse({"task_id": response.id}, status_code=200)


@router.get("/task/{task_id}")
async def get_task_status(task_id: str) -> dict[str, Any]:
    return get_task_info(task_id)
