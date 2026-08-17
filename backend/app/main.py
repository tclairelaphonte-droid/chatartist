from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.config import settings
from app.database import Base, engine
from app.routers import auth, artists, conversations, manager, uploads, ws, admin


Base.metadata.create_all(bind=engine)

Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="Backstage API",
    description="API de la plateforme communautaire — fans, artistes, messagerie, managers, admin.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/files", StaticFiles(directory=settings.upload_dir), name="files")

app.include_router(auth.router)
app.include_router(artists.router)
app.include_router(conversations.router)
app.include_router(manager.router)
app.include_router(uploads.router)
app.include_router(ws.router)
app.include_router(admin.router)


@app.get("/health")
def health():
    return {"status": "ok"}