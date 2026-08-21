import cloudinary
import cloudinary.uploader

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.database import get_db
from app.deps import require_fan
from app.models import Artist, Conversation, Message, SenderType, User
from app.schemas import (
    ConversationDetailOut,
    ConversationOut,
    MessageOut,
    SendMessageIn,
)
from app.ws_manager import manager as ws_manager


# ---------------------------------------------------------------------------
# Configuration Cloudinary (IMPORTANT)
# ---------------------------------------------------------------------------

cloudinary.config(
    cloud_name=settings.cloudinary_cloud_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret,
    secure=True,
)


router = APIRouter(
    prefix="/conversations",
    tags=["conversations"],
)


# ---------------------------------------------------------------------------
# Images
# ---------------------------------------------------------------------------

ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}

MAX_IMAGE_BYTES = settings.max_upload_size_mb * 1024 * 1024


def _save_chat_image(file: UploadFile) -> str:
    """
    Envoie l'image du fan vers Cloudinary
    et retourne son URL HTTPS publique.
    """

    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Format d'image non supporté. Utilisez JPEG, PNG, WebP ou GIF.",
        )

    data = file.file.read()

    if not data:
        raise HTTPException(
            status_code=400,
            detail="Le fichier envoyé est vide.",
        )

    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Image trop volumineuse "
                f"(max {settings.max_upload_size_mb} Mo)."
            ),
        )

    try:
        result = cloudinary.uploader.upload(
            data,
            folder="artistchat/chat",
            resource_type="image",
        )

        secure_url = result.get("secure_url")

        if not secure_url:
            raise RuntimeError("Cloudinary n'a pas retourné de secure_url.")

        return secure_url

    except HTTPException:
        raise

    except Exception as e:
        print("Cloudinary upload error:", repr(e))

        raise HTTPException(
            status_code=500,
            detail="Impossible d'envoyer l'image.",
        )


# ---------------------------------------------------------------------------
# Conversations
# ---------------------------------------------------------------------------

def _get_owned_conversation(
    db: Session,
    conversation_id: str,
    fan_id: str,
) -> Conversation:
    """
    Vérifie que la conversation appartient bien au fan connecté.
    """

    conversation = (
        db.query(Conversation)
        .options(
            joinedload(Conversation.messages),
        )
        .filter(
            Conversation.id == conversation_id,
        )
        .first()
    )

    if not conversation or conversation.fan_id != fan_id:
        raise HTTPException(
            status_code=404,
            detail="Conversation introuvable.",
        )

    return conversation


def _sorted_messages(messages):
    """
    Retourne les messages dans l'ordre chronologique.
    """

    return sorted(
        list(messages or []),
        key=lambda m: (
            m.created_at
            or datetime.min.replace(tzinfo=timezone.utc)
        ),
    )


# ---------------------------------------------------------------------------
# Boîte de réception du fan
# ---------------------------------------------------------------------------

@router.get(
    "",
    response_model=list[ConversationOut],
)
def list_my_conversations(
    db: Session = Depends(get_db),
    current_fan: User = Depends(require_fan),
):
    """
    Liste toutes les conversations du fan connecté.

    Les conversations sont triées par dernière activité.
    """

    conversations = (
        db.query(Conversation)
        .options(
            joinedload(Conversation.artist),
            joinedload(Conversation.messages),
        )
        .filter(
            Conversation.fan_id == current_fan.id,
        )
        .order_by(
            Conversation.updated_at.desc(),
        )
        .all()
    )

    results = []

    for conversation in conversations:

        if not conversation.artist:
            continue

        messages = _sorted_messages(
            conversation.messages
        )

        last_message = (
            messages[-1]
            if messages
            else None
        )

        # ---------------------------------------------------------------
        # Messages manager non lus
        # ---------------------------------------------------------------

        unread = 0

        last_fan_index = -1

        for index, message in enumerate(messages):
            if message.sender_type == SenderType.fan:
                last_fan_index = index

        for message in messages[last_fan_index + 1:]:
            if message.sender_type == SenderType.manager:
                unread += 1

        # ---------------------------------------------------------------
        # Informations du fan
        # ---------------------------------------------------------------

        fan_username = (
            current_fan.username
            or (
                current_fan.email.split("@")[0]
                if current_fan.email
                else "fan"
            )
        )

        fan_avatar_url = getattr(
            current_fan,
            "avatar_url",
            None,
        )

        # ---------------------------------------------------------------
        # Résultat
        # ---------------------------------------------------------------

        results.append(
            ConversationOut(
                id=conversation.id,
                artist_id=conversation.artist.id,
                artist_name=conversation.artist.name,
                fan_id=current_fan.id,
                fan_username=fan_username,
                fan_avatar_url=fan_avatar_url,
                last_message=(
                    MessageOut.model_validate(last_message)
                    if last_message
                    else None
                ),
                unread_count=unread,
                updated_at=(
                    conversation.updated_at
                    or conversation.created_at
                    or datetime.now(timezone.utc)
                ),
            )
        )

    return results


# ---------------------------------------------------------------------------
# Démarrer / récupérer une conversation
# ---------------------------------------------------------------------------

@router.post(
    "/start/{artist_id}",
    response_model=ConversationDetailOut,
)
def start_or_get_conversation(
    artist_id: str,
    db: Session = Depends(get_db),
    current_fan: User = Depends(require_fan),
):
    """
    Crée une conversation avec un artiste si elle n'existe pas.
    Sinon retourne la conversation existante.
    """

    artist = (
        db.query(Artist)
        .filter(
            Artist.id == artist_id,
        )
        .first()
    )

    if not artist:
        raise HTTPException(
            status_code=404,
            detail="Artiste introuvable.",
        )

    conversation = (
        db.query(Conversation)
        .options(
            joinedload(Conversation.messages),
        )
        .filter(
            Conversation.fan_id == current_fan.id,
            Conversation.artist_id == artist_id,
        )
        .first()
    )

    if not conversation:

        conversation = Conversation(
            fan_id=current_fan.id,
            artist_id=artist_id,
        )

        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        conversation = (
            db.query(Conversation)
            .options(
                joinedload(Conversation.messages),
            )
            .filter(
                Conversation.id == conversation.id,
            )
            .first()
        )

    return ConversationDetailOut(
        id=conversation.id,
        artist=artist,
        messages=list(
            conversation.messages or []
        ),
    )


# ---------------------------------------------------------------------------
# Messages d'une conversation
# ---------------------------------------------------------------------------

@router.get(
    "/{conversation_id}/messages",
    response_model=list[MessageOut],
)
def get_messages(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_fan: User = Depends(require_fan),
):
    """
    Récupère tous les messages d'une conversation.
    """

    conversation = _get_owned_conversation(
        db,
        conversation_id,
        current_fan.id,
    )

    return _sorted_messages(
        conversation.messages
    )


# ---------------------------------------------------------------------------
# Upload d'une image dans une conversation
# ---------------------------------------------------------------------------

@router.post(
    "/{conversation_id}/image",
)
async def upload_chat_image(
    conversation_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_fan: User = Depends(require_fan),
):
    """
    Upload d'une image envoyée par le fan.

    L'image est stockée sur Cloudinary.
    """

    _get_owned_conversation(
        db,
        conversation_id,
        current_fan.id,
    )

    image_url = _save_chat_image(file)

    return {
        "image_url": image_url,
    }


# ---------------------------------------------------------------------------
# Envoyer un message
# ---------------------------------------------------------------------------

@router.post(
    "/{conversation_id}/messages",
    response_model=MessageOut,
    status_code=201,
)
async def send_message(
    conversation_id: str,
    payload: SendMessageIn,
    db: Session = Depends(get_db),
    current_fan: User = Depends(require_fan),
):
    """
    Envoie un message texte et/ou une image.
    """

    conversation = _get_owned_conversation(
        db,
        conversation_id,
        current_fan.id,
    )

    # Au moins du texte ou une image
    if not payload.text and not payload.image_url:
        raise HTTPException(
            status_code=400,
            detail="Le message doit contenir du texte ou une photo.",
        )

    message = Message(
        conversation_id=conversation.id,
        sender_type=SenderType.fan,
        text=payload.text,
        image_url=payload.image_url,
        read_by_manager=False,
    )

    db.add(message)

    conversation.updated_at = datetime.now(
        timezone.utc
    )

    db.commit()
    db.refresh(message)

    # ---------------------------------------------------------------
    # WebSocket : prévenir le manager en temps réel
    # ---------------------------------------------------------------

    out = MessageOut.model_validate(message)

    await ws_manager.broadcast(
        conversation.id,
        out.model_dump(mode="json"),
    )

    return out