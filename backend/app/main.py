from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

# Роутеры
from app.api.v1.routers.auth import router as auth_router
from app.api.v1.routers.managers import router as manager_router
from app.api.v1.routers.person import router as person_router
from app.api.v1.routers.artist import router as artist_router
from app.api.v1.routers.album import router as album_router
from app.api.v1.routers.track import router as track_router
from app.api.v1.routers.drafts import router as drafts_router
from app.database import DBSessionDep
from app.deps import AuthUserDep
from app.services.startup import create_first_admin
from app.sqlmodels.user import User

app = FastAPI(
    title="Music Rights Management API",
    version="0.1.0",
)

@app.on_event("startup")
async def startup():
    await create_first_admin()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3002",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Все роутеры подключены с префиксом /api/v1
app.include_router(auth_router, prefix="/api/v1")
app.include_router(manager_router, prefix="/api/v1")
app.include_router(person_router, prefix="/api/v1")
app.include_router(artist_router, prefix="/api/v1")
app.include_router(album_router, prefix="/api/v1")
app.include_router(track_router, prefix="/api/v1")
app.include_router(drafts_router, prefix="/api/v1")

@app.get("/test")
async def test_connection():
    return {"message": "Соединение с бекендом успешно!"}

@app.get("/")
async def root():
    return {"project": "music_manager", "status": "✅ connected"}

@app.get("/debug-test")
async def debug_test(
    db_session: DBSessionDep,
    current_user: User = Depends(AuthUserDep),
):
    return {
        "status": "Dependencies work!",
        "user_email": current_user.email,
        "user_role": current_user.role
    }