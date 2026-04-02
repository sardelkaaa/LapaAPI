from fastapi import APIRouter, Depends, UploadFile, File
from app.api.v1.deps import get_current_user
from app.models.user import UserOut, UserUpdateRequests
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