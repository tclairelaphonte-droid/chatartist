import os
import uuid

import cloudinary
import cloudinary.uploader

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from app.config import settings
from app.database import get_db
from app.deps import require_manager
from app.models import Artist, User


router = APIRouter(prefix="/manager/artists", tags=["manager-uploads"])

ALLOWED_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
}

MAX_BYTES = settings.max_upload_size_mb * 1024 * 1024


# Cloudinary utilise les 3 variables d'environnement séparées
# configurées dans Vercel.
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True,
)


async def _upload_image(file: UploadFile, subdir: str) -> str:
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Format non supporté. Utilisez JPEG, PNG, WebP ou GIF.",
        )

    data = await file.read()

    if len(data) > MAX_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"Fichier trop volumineux (max {settings.max_upload_size_mb} Mo).",
        )

    try:
        result = cloudinary.uploader.upload(
            data,
            folder=f"chatartist/{subdir}",
            public_id=uuid.uuid4().hex,
            resource_type="image",
        )

        secure_url = result.get("secure_url")

        if not secure_url:
            raise RuntimeError("Cloudinary n'a pas retourné d'URL.")

        return secure_url

    except Exception as exc:
        print(f"Cloudinary upload error: {exc}")
        raise HTTPException(
            status_code=500,
            detail="Impossible d'envoyer l'image.",
        )


def _owned_artist(db: Session, artist_id: str, manager: User) -> Artist:
    artist = (
        db.query(Artist)
        .filter(
            Artist.id == artist_id,
            Artist.manager_id == manager.id,
        )
        .first()
    )

    if not artist:
        raise HTTPException(
            status_code=404,
            detail="Artiste introuvable.",
        )

    return artist


@router.post("/{artist_id}/avatar")
async def upload_avatar(
    artist_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_manager: User = Depends(require_manager),
):
    artist = _owned_artist(db, artist_id, current_manager)

    url = await _upload_image(
        file,
        f"managers/{current_manager.id}/avatars",
    )

    artist.avatar_url = url

    db.commit()
    db.refresh(artist)

    return {"avatar_url": artist.avatar_url}


@router.post("/{artist_id}/cover")
async def upload_cover(
    artist_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_manager: User = Depends(require_manager),
):
    artist = _owned_artist(db, artist_id, current_manager)

    url = await _upload_image(
        file,
        f"managers/{current_manager.id}/covers",
    )

    artist.cover_url = url

    db.commit()
    db.refresh(artist)

    return {"cover_url": artist.cover_url}


@router.post("/{artist_id}/gallery")
async def upload_gallery_image(
    artist_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_manager: User = Depends(require_manager),
):
    artist = _owned_artist(db, artist_id, current_manager)

    url = await _upload_image(
        file,
        f"managers/{current_manager.id}/gallery",
    )

    gallery = list(artist.gallery or [])
    gallery.append(url)

    artist.gallery = gallery
    flag_modified(artist, "gallery")

    db.commit()
    db.refresh(artist)

    return {
        "url": url,
        "gallery": artist.gallery,
    }


@router.delete("/{artist_id}/gallery")
def remove_gallery_image(
    artist_id: str,
    url: str,
    db: Session = Depends(get_db),
    current_manager: User = Depends(require_manager),
):
    artist = _owned_artist(db, artist_id, current_manager)

    gallery = [
        u for u in (artist.gallery or [])
        if u != url
    ]

    artist.gallery = gallery
    flag_modified(artist, "gallery")

    db.commit()
    db.refresh(artist)

    return {"gallery": artist.gallery}