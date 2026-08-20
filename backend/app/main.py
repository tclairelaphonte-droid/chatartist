from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import artists
from app.routers import auth
from app.routers import admin
from app.routers import conversations
from app.routers import manager
from app.routers import uploads
from app.routers import ws


app = FastAPI(
    title="ArtistChat API",
    version="0.1.0",
)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routes publiques
app.include_router(artists.router)

# Auth
app.include_router(auth.router, prefix="/api/auth")

# Fan
app.include_router(conversations.router)

# Manager
app.include_router(manager.router)

# Uploads manager
app.include_router(uploads.router)

# WebSocket
app.include_router(ws.router)

# Admin
app.include_router(admin.router)


@app.get("/")
def root():
    return {
        "status": "OK",
        "message": "ArtistChat backend fonctionne"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }