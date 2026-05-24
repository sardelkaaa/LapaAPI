from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.admin import router as admin_router
from app.api.v1.volunteer import router as volunteer_router
from app.api.v1.tasks import router as tasks_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from app.api.v1.animals import router as animals_router
from app.api.v1.calendar import router as calendar_router
from app.api.v1.reviews import router as reviews_router
from app.api.v1.chats import router as chats_router
from app.api.v1.articles import router as articles_router
from app.socketio_server import socket_app

app = FastAPI(title=settings.APP_NAME,
              description="API для волонтерского проекта",
              debug=settings.DEBUG)

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8000",
    "http://localhost:8080",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8080",
    "https://lapa-frontend.amvera.io",
    "https://lapa-api-delderol.amvera.io",
    "https://lapafrontend.onrender.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/socket.io", socket_app)

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(admin_router)
app.include_router(volunteer_router)
app.include_router(animals_router)
app.include_router(tasks_router)
app.include_router(calendar_router)
app.include_router(reviews_router)
app.include_router(articles_router)

app.include_router(chats_router, prefix="/api/v1")