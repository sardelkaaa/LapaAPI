from typing import Optional, List
from fastapi import APIRouter, Depends, UploadFile, File, Query
from app.api.v1.deps import get_current_user
from app.models.user import UserOut, UserUpdateRequests, OrganizationListResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserOut)
def get_me(current_user=Depends(get_current_user)):
    return UserService.get_me(current_user)


@router.patch("/me", response_model=UserOut)
def update_me(
    payload: UserUpdateRequests,
    current_user=Depends(get_current_user),
):
    return UserService.update_me(current_user["id"], payload.model_dump(exclude_unset=True))


@router.delete("/me")
def delete_me(current_user=Depends(get_current_user)):
    return UserService.delete_me(current_user["id"])


@router.post("/me/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
):
    return await UserService.upload_avatar(current_user["id"], file)

@router.get("", response_model=OrganizationListResponse)
def get_organizations(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: Optional[str] = None,
    current_user=Depends(get_current_user)  # любой авторизованный
):
    """Получить список всех организаций"""
    return UserService.get_organizations(limit, offset, search)