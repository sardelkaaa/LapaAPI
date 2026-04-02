from fastapi import APIRouter, Depends, HTTPException, status
from app.api.v1.deps import require_roles
from app.db.repositories.users import UsersRepository
from app.models.user import UserOut

router = APIRouter(prefix="/admin", tags=["Admin"])
