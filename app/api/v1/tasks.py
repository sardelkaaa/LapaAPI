from fastapi import APIRouter, Depends, Query, status
from app.api.v1.deps import get_current_user, require_roles
from app.services.task_service import TaskService
from app.models.task import TaskCreate, TaskOut, TaskUpdate, TaskListResponse

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, current_user=Depends(require_roles("curator", "organization", "admin"))):
    """Создать задание. Может только админ, куратор или организация"""
    return TaskService.create_task(current_user, payload.model_dump(exclude_none=True))

@router.get("", response_model=TaskListResponse)
def list_tasks(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user=Depends(get_current_user)
):
    return TaskService.list_tasks(current_user, limit, offset)

@router.get("/recommendations", response_model=TaskListResponse)
def recommend_tasks(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user=Depends(require_roles("volunteer"))
):
    """Рекомендуемые задания для волонтера по его предпочтениям"""
    return TaskService.recommend_tasks(current_user, limit, offset)

@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: str):
    """Получение всех заданий \"в ожидании\" и своих созданных"""
    return TaskService.get_task(task_id)

@router.put("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: str,
    payload: TaskUpdate,
    current_user=Depends(require_roles("curator", "organization", "admin"))
):
    """Обновление данных задания. Может только админ, куратор или организация"""
    return TaskService.update_task(current_user, task_id, payload.model_dump(exclude_unset=True))

@router.post("/{task_id}/take", response_model=TaskOut)
def take_task(task_id: str, current_user=Depends(require_roles("volunteer"))):
    """Взять задание. Может только волонтёр"""
    return TaskService.take_task(current_user, task_id)

@router.post("/{task_id}/cancel", response_model=TaskOut)
def cancel_task(task_id: str, current_user=Depends(get_current_user)):
    """Отменить задание и возвращение статуса \"в ожидании\"."""
    return TaskService.cancel_task(current_user, task_id)

@router.post("/{task_id}/complete", response_model=TaskOut)
def complete_task(task_id: str, current_user=Depends(require_roles("volunteer"))):
    """Завершить задание и возвращение статуса \"в ожидании\"."""
    return TaskService.complete_task(current_user, task_id)