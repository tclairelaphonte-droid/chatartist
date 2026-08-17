from datetime import datetime, timezone
from pathlib import Path
import uuid

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

router = APIRouter(prefix="/conversations", tags=["conversations"])

ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}

MAX_IMAGE_BYTES = settings.max_upload_size_mb * 1024 * 1024


def _save_chat_image(file: UploadFile) -> str:
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Format d'image non supporté. Utilisez JPEG, PNG, WebP ou GIF.",
        )

    data = file.file.read()

    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"Image trop volumineuse (max {settings.max_upload_size_mb} Mo).",
        )

    ext = ALLOWED_IMAGE_TYPES[file.content_type]

    folder = Path(settings.upload_dir) / "chat"
    folder.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid.uuid4().hex}{ext}"
    path = folder / filename
    path.write_bytes(data)

    return f"/files/chat/{filename}"


def _get_owned_conversation(db: Session, conversation_id: str, fan_id: str) -> Conversation:
    conversation = (
        db.query(Conversation)
        .options(joinedload(Conversation.messages))
        .filter(Conversation.id == conversation_id)
        .first()
    )
    if not conversation or conversation.fan_id != fan_id:
        raise HTTPException(status_code=404, detail="Conversation introuvable.")
    return conversation


def _sorted_messages(messages):
    return sorted(
        list(messages or []),
        key=lambda m: m.created_at or datetime.min.replace(tzinfo=timezone.utc),
    )


# ---------------------------------------------------------------------------
# Boîte de réception du fan — DOIT rester AVANT /{conversation_id}/...
# ---------------------------------------------------------------------------
@router.get("", response_model=list[ConversationOut])
def list_my_conversations(
    db: Session = Depends(get_db),
    current_fan: User = Depends(require_fan),
):
    """
    Liste toutes les conversations du fan connecté,
    pour affichage sur l'accueil (réponses manager visibles après reconnexion).
    """
    conversations = (
        db.query(Conversation)
        .options(
            joinedload(Conversation.artist),
            joinedload(Conversation.messages),
        )
        .filter(Conversation.fan_id == current_fan.id)
        .order_by(Conversation.updated_at.desc())
        .all()
    )

    results = []
    for c in conversations:
        if not c.artist:
            continue

        msgs = _sorted_messages(c.messages)
        last = msgs[-1] if msgs else None

        # Non-lus simples : messages manager après le dernier message fan
        unread = 0
        last_fan_idx = -1
        for i, m in enumerate(msgs):
            if m.sender_type == SenderType.fan:
                last_fan_idx = i
        for m in msgs[last_fan_idx + 1 :]:
            if m.sender_type == SenderType.manager:
                unread += 1

        results.append(
            ConversationOut(
                id=c.id,
                artist_id=c.artist.id,
                artist_name=c.artist.name,
                fan_id=current_fan.id,
                fan_username=current_fan.username
                or (current_fan.email.split("@")[0] if current_fan.email else "fan"),
                fan_avatar_url=getattr(current_fan, "avatar_url", None),
                last_message=MessageOut.model_validate(last) if last else None,
                unread_count=unread,
                updated_at=c.updated_at or c.created_at or datetime.now(timezone.utc),
            )
        )
    return results


@router.post("/{conversation_id}/image")
async def upload_chat_image(
    conversation_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_fan: User = Depends(require_fan),
):
    conversation = _get_owned_conversation(
        db,
        conversation_id,
        current_fan.id,
    )
    image_url = _save_chat_image(file)
    return {"image_url": image_url}


@router.post("/start/{artist_id}", response_model=ConversationDetailOut)
def start_or_get_conversation(
    artist_id: str,
    db: Session = Depends(get_db),
    current_fan: User = Depends(require_fan),
):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artiste introuvable.")

    conversation = (
        db.query(Conversation)
        .options(joinedload(Conversation.messages))
        .filter(
            Conversation.fan_id == current_fan.id,
            Conversation.artist_id == artist_id,
        )
        .first()
    )
    if not conversation:
        conversation = Conversation(fan_id=current_fan.id, artist_id=artist_id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        conversation = (
            db.query(Conversation)
            .options(joinedload(Conversation.messages))
            .filter(Conversation.id == conversation.id)
            .first()
        )

    return ConversationDetailOut(
        id=conversation.id,
        artist=artist,
        messages=list(conversation.messages or []),
    )


@router.get("/{conversation_id}/messages", response_model=list[MessageOut])
def get_messages(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_fan: User = Depends(require_fan),
):
    conversation = _get_owned_conversation(db, conversation_id, current_fan.id)
    return _sorted_messages(conversation.messages)


@router.post("/{conversation_id}/messages", response_model=MessageOut, status_code=201)
async def send_message(
    conversation_id: str,
    payload: SendMessageIn,
    db: Session = Depends(get_db),
    current_fan: User = Depends(require_fan),
):
    conversation = _get_owned_conversation(db, conversation_id, current_fan.id)
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
    conversation.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(message)

    out = MessageOut.model_validate(message)
    await ws_manager.broadcast(conversation.id, out.model_dump(mode="json"))
    return out