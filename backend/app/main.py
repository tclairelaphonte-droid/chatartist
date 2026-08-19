from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import artists
from app.routers import auth
from app.routers import admin
from app.routers import manager
from app.routers import uploads

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

# Authentification
app.include_router(auth.router, prefix="/api/auth")

# Administration
app.include_router(admin.router)

# Espace manager
app.include_router(manager.router)

# Uploads manager
app.include_router(uploads.router)


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