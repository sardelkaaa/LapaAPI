from fastapi import FastAPI, WebSocket, Query
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
from app.api.v1.websocket import websocket_endpoint
from app.api.v1.chats import router as chats_router
from app.api.v1.articles import router as articles_router

app = FastAPI(title=settings.APP_NAME,
              description="API для волонтерского проекта",
              debug=settings.DEBUG)

origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
app.add_api_websocket_route("/ws", websocket_endpoint)