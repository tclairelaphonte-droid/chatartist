from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from app.routers import artists
from app.routers import auth


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
app.include_router(artists.router)
app.include_router(auth.router, prefix="/api/auth")


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
