from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Artist, Conversation, Message
from app.schemas import ArtistOut, ArtistWithCount

router = APIRouter(prefix="/artists", tags=["artists"])


@router.get("", response_model=list[ArtistWithCount])
def list_artists(db: Session = Depends(get_db)):
    """
    Page d'accueil fan : uniquement les artistes publiés
    (tous managers confondus, mais isolés côté conversations).
    """
    artists = (
        db.query(Artist)
        .filter(Artist.is_published.is_(True))
        .order_by(Artist.name.asc())
        .all()
    )
    results = []
    for artist in artists:
        conv_count = (
            db.query(func.count(Conversation.id))
            .filter(Conversation.artist_id == artist.id)
            .scalar()
        )
        msg_count = (
            db.query(func.count(Message.id))
            .join(Conversation, Message.conversation_id == Conversation.id)
            .filter(Conversation.artist_id == artist.id)
            .scalar()
        )
        results.append(
            ArtistWithCount(
                **ArtistOut.model_validate(artist).model_dump(),
                conversation_count=conv_count or 0,
                message_count=msg_count or 0,
            )
        )
    return results


@router.get("/{artist_id}", response_model=ArtistOut)
def get_artist(artist_id: str, db: Session = Depends(get_db)):
    """Profil public : artiste publié uniquement."""
    artist = (
        db.query(Artist)
        .filter(Artist.id == artist_id, Artist.is_published.is_(True))
        .first()
    )
    if not artist:
        raise HTTPException(status_code=404, detail="Artiste introuvable.")
    return artist