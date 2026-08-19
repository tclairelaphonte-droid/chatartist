from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import artists, auth, conversations, manager, admin, uploads

app = FastAPI(
    title="ArtistChat API",
    version="0.1.0",
)

# CORS (pour que ton frontend Netlify puisse appeler le backend Vercel)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(artists.router, prefix="/api/artists", tags=["artists"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(conversations.router, prefix="/api/conversations", tags=["conversations"])
app.include_router(manager.router, prefix="/api/manager", tags=["manager"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(uploads.router, prefix="/api/uploads", tags=["uploads"])

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
