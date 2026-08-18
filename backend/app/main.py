from fastapi import FastAPI

app = FastAPI(
    title="ArtistChat API",
    version="0.1.0",
)

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