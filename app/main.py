from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.admin import router as admin_router

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(admin_router)