import re
from datetime import datetime, timezone

import cloudinary
import cloudinary.uploader

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Request,
    UploadFile,
)
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.deps import require_manager
from app.models import (
    Artist,
    Conversation,
    Message,
    SenderType,
    User,
    UserRole,
)
from app.schemas import (
    ArtistOut,
    ArtistCreateIn,
    ArtistUpdateIn,
    ConversationOut,
    MessageOut,
    SendMessageIn,
)
from app.ws_manager import manager as ws_manager


router = APIRouter(prefix="/manager", tags=["manager"])


# ---------------------------------------------------------------------------
# CLOUDINARY
# ---------------------------------------------------------------------------

ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}

MAX_IMAGE_BYTES = 5 * 1024 * 1024


def _save_chat_image(file: UploadFile) -> str:
    """
    Envoie une image de conversation vers Cloudinary
    et retourne son URL HTTPS publique.
    """

    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=(
                "Format d'image non supporté. "
                "Utilisez JPEG, PNG, WebP ou GIF."
            ),
        )

    data = file.file.read()

    if not data:
        raise HTTPException(
            status_code=400,
            detail="Le fichier image est vide.",
        )

    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(
            status_code=400,
            detail="Image trop volumineuse (max 5 Mo).",
        )

    try:
        result = cloudinary.uploader.upload(
            data,
            folder="artistchat/chat",
            resource_type="image",
            secure=True,
        )

        secure_url = result.get("secure_url")

        if not secure_url:
            raise RuntimeError("Cloudinary n'a pas retourné de secure_url.")

        return secure_url

    except Exception as e:
        print("Cloudinary upload error:", repr(e))

        raise HTTPException(
            status_code=500,
            detail="Impossible d'envoyer l'image.",
        )


# ---------------------------------------------------------------------------
# UTILITAIRES MANAGER
# ---------------------------------------------------------------------------

def _acting_manager_id(
    request: Request,
    current: User,
    db: Session,
) -> str:
    """
    Manager :
        -> utilise son propre ID.

    Admin + X-Act-As-Manager :
        -> agit au nom du manager indiqué.

    Admin sans header :
        -> utilise son propre ID.
    """

    if current.role == UserRole.admin:
        act = request.headers.get("X-Act-As-Manager")

        if act:
            manager = (
                db.query(User)
                .filter(
                    User.id == act,
                    User.role == UserRole.manager,
                )
                .first()
            )

            if not manager:
                raise HTTPException(
                    status_code=404,
                    detail="Manager introuvable.",
                )

            return manager.id

    return current.id


def _get_owned_artist(
    db: Session,
    artist_id: str,
    manager_id: str,
) -> Artist:

    artist = (
        db.query(Artist)
        .filter(
            Artist.id == artist_id,
            Artist.manager_id == manager_id,
        )
        .first()
    )

    if not artist:
        raise HTTPException(
            status_code=404,
            detail="Artiste introuvable.",
        )

    return artist


def _get_owned_conversation(
    db: Session,
    conversation_id: str,
    manager_id: str,
) -> Conversation:

    conversation = (
        db.query(Conversation)
        .options(
            joinedload(Conversation.artist),
            joinedload(Conversation.messages),
            joinedload(Conversation.fan),
        )
        .filter(
            Conversation.id == conversation_id
        )
        .first()
    )

    if not conversation or not conversation.artist:
        raise HTTPException(
            status_code=404,
            detail="Conversation introuvable.",
        )

    if conversation.artist.manager_id != manager_id:
        raise HTTPException(
            status_code=404,
            detail="Conversation introuvable.",
        )

    return conversation


def _slugify(name: str) -> str:
    s = name.lower().strip()

    s = re.sub(
        r"[^a-z0-9\s-]",
        "",
        s,
    )

    s = re.sub(
        r"[\s_-]+",
        "-",
        s,
    )

    s = s.strip("-")

    return s[:60] or "artiste"


def _unique_slug(
    db: Session,
    base: str,
    exclude_id: str | None = None,
) -> str:

    slug = base
    n = 2

    while True:

        q = (
            db.query(Artist)
            .filter(Artist.slug == slug)
        )

        if exclude_id:
            q = q.filter(
                Artist.id != exclude_id
            )

        if not q.first():
            return slug

        slug = f"{base}-{n}"
        n += 1


def _sorted_messages(messages):
    return sorted(
        list(messages or []),
        key=lambda m: (
            m.created_at
            or datetime.min.replace(
                tzinfo=timezone.utc
            )
        ),
    )


# ---------------------------------------------------------------------------
# SERIALISATION CONVERSATION
# ---------------------------------------------------------------------------

def _conversation_out(
    c: Conversation,
    artist: Artist,
) -> ConversationOut:

    msgs = _sorted_messages(c.messages)

    last = msgs[-1] if msgs else None

    unread = sum(
        1
        for m in msgs
        if (
            m.sender_type == SenderType.fan
            and not m.read_by_manager
        )
    )

    fan = c.fan

    fan_username = "fan"
    fan_avatar = None
    fan_id = c.fan_id

    if fan:

        fan_username = (
            fan.username
            or (
                fan.email.split("@")[0]
                if fan.email
                else "fan"
            )
        )

        fan_avatar = getattr(
            fan,
            "avatar_url",
            None,
        )

        fan_id = fan.id

    return ConversationOut(
        id=c.id,
        artist_id=artist.id,
        artist_name=artist.name,
        fan_id=fan_id,
        fan_username=fan_username,
        fan_avatar_url=fan_avatar,
        last_message=(
            MessageOut.model_validate(last)
            if last
            else None
        ),
        unread_count=unread,
        updated_at=(
            c.updated_at
            or c.created_at
            or datetime.now(timezone.utc)
        ),
    )


def _artist_out_with_unread(
    db: Session,
    a: Artist,
) -> ArtistOut:

    unread = (
        db.query(func.count(Message.id))
        .join(
            Conversation,
            Message.conversation_id
            == Conversation.id,
        )
        .filter(
            Conversation.artist_id == a.id,
            Conversation.trashed_at.is_(None),
            Message.sender_type
            == SenderType.fan,
            Message.read_by_manager.is_(False),
        )
        .scalar()
    ) or 0

    data = (
        ArtistOut
        .model_validate(a)
        .model_dump()
    )

    data["unread_count"] = unread

    return ArtistOut(**data)


# ===========================================================================
# ARTISTES
# ===========================================================================

@router.get(
    "/artists",
    response_model=list[ArtistOut],
)
def list_my_artists(
    request: Request,
    db: Session = Depends(get_db),
    current_manager: User = Depends(require_manager),
):

    mid = _acting_manager_id(
        request,
        current_manager,
        db,
    )

    artists = (
        db.query(Artist)
        .filter(
            Artist.manager_id == mid
        )
        .order_by(
            Artist.name.asc()
        )
        .all()
    )

    return [
        _artist_out_with_unread(db, a)
        for a in artists
    ]


@router.get(
    "/artists/{artist_id}",
    response_model=ArtistOut,
)
def get_my_artist(
    artist_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_manager: User = Depends(require_manager),
):

    mid = _acting_manager_id(
        request,
        current_manager,
        db,
    )

    artist = _get_owned_artist(
        db,
        artist_id,
        mid,
    )

    return _artist_out_with_unread(
        db,
        artist,
    )


@router.post(
    "/artists",
    response_model=ArtistOut,
    status_code=201,
)
def create_artist(
    payload: ArtistCreateIn,
    request: Request,
    db: Session = Depends(get_db),
    current_manager: User = Depends(require_manager),
):

    mid = _acting_manager_id(
        request,
        current_manager,
        db,
    )

    base_slug = (
        payload.slug
        or _slugify(payload.name)
    )

    slug = _unique_slug(
        db,
        base_slug,
    )

    artist = Artist(
        manager_id=mid,
        name=payload.name,
        slug=slug,
        genre=payload.genre,
        bio_short=payload.bio_short,
        bio_full=payload.bio_full,
        avatar_url=payload.avatar_url,
        cover_url=payload.cover_url,
        is_published=payload.is_published,
        gallery=payload.gallery,
        tracks=payload.tracks,
        clips=payload.clips,
        news=payload.news,
    )

    db.add(artist)
    db.commit()
    db.refresh(artist)

    return _artist_out_with_unread(
        db,
        artist,
    )


@router.patch(
    "/artists/{artist_id}",
    response_model=ArtistOut,
)
def update_artist(
    artist_id: str,
    payload: ArtistUpdateIn,
    request: Request,
    db: Session = Depends(get_db),
    current_manager: User = Depends(require_manager),
):

    mid = _acting_manager_id(
        request,
        current_manager,
        db,
    )

    artist = _get_owned_artist(
        db,
        artist_id,
        mid,
    )

    data = payload.model_dump(
        exclude_unset=True
    )

    if "slug" in data and data["slug"]:
        data["slug"] = _unique_slug(
            db,
            data["slug"],
            exclude_id=artist.id,
        )

    for key, value in data.items():
        setattr(
            artist,
            key,
            value,
        )

    db.commit()
    db.refresh(artist)

    return _artist_out_with_unread(
        db,
        artist,
    )


@router.delete(
    "/artists/{artist_id}",
    status_code=204,
)
def delete_artist(
    artist_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_manager: User = Depends(require_manager),
):

    mid = _acting_manager_id(
        request,
        current_manager,
        db,
    )

    artist = _get_owned_artist(
        db,
        artist_id,
        mid,
    )

    db.delete(artist)
    db.commit()

    return None


# ===========================================================================
# CONVERSATIONS
# ===========================================================================

@router.get(
    "/artists/{artist_id}/conversations",
    response_model=list[ConversationOut],
)
def conversations_for_artist(
    artist_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_manager: User = Depends(require_manager),
):

    mid = _acting_manager_id(
        request,
        current_manager,
        db,
    )

    artist = _get_owned_artist(
        db,
        artist_id,
        mid,
    )

    conversations = (
        db.query(Conversation)
        .options(
            joinedload(
                Conversation.fan
            ),
            joinedload(
                Conversation.messages
            ),
        )
        .filter(
            Conversation.artist_id == artist_id,
            Conversation.trashed_at.is_(None),
        )
        .order_by(
            Conversation.updated_at.desc()
        )
        .all()
    )

    return [
        _conversation_out(c, artist)
        for c in conversations
    ]


@router.get(
    "/artists/{artist_id}/conversations/trash",
    response_model=list[ConversationOut],
)
def trash_conversations_for_artist(
    artist_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_manager: User = Depends(require_manager),
):

    mid = _acting_manager_id(
        request,
        current_manager,
        db,
    )

    artist = _get_owned_artist(
        db,
        artist_id,
        mid,
    )

    conversations = (
        db.query(Conversation)
        .options(
            joinedload(
                Conversation.fan
            ),
            joinedload(
                Conversation.messages
            ),
        )
        .filter(
            Conversation.artist_id == artist_id,
            Conversation.trashed_at.is_not(None),
        )
        .order_by(
            Conversation.updated_at.desc()
        )
        .all()
    )

    return [
        _conversation_out(c, artist)
        for c in conversations
    ]


# ===========================================================================
# MESSAGES
# ===========================================================================

@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=list[MessageOut],
)
def get_conversation_messages(
    conversation_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_manager: User = Depends(require_manager),
):

    mid = _acting_manager_id(
        request,
        current_manager,
        db,
    )

    conversation = _get_owned_conversation(
        db,
        conversation_id,
        mid,
    )

    msgs = _sorted_messages(
        conversation.messages
    )

    changed = False

    for message in msgs:

        if (
            message.sender_type
            == SenderType.fan
            and not message.read_by_manager
        ):
            message.read_by_manager = True
            changed = True

    if changed:
        db.commit()

    return [
        MessageOut.model_validate(m)
        for m in msgs
    ]


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=MessageOut,
    status_code=201,
)
async def reply_to_conversation(
    conversation_id: str,
    payload: SendMessageIn,
    request: Request,
    db: Session = Depends(get_db),
    current_manager: User = Depends(require_manager),
):

    mid = _acting_manager_id(
        request,
        current_manager,
        db,
    )

    conversation = _get_owned_conversation(
        db,
        conversation_id,
        mid,
    )

    if (
        not payload.text
        and not payload.image_url
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Le message doit contenir "
                "du texte ou une photo."
            ),
        )

    message = Message(
        conversation_id=conversation.id,
        sender_type=SenderType.manager,
        text=payload.text,
        image_url=payload.image_url,
        read_by_manager=True,
    )

    db.add(message)

    conversation.updated_at = (
        datetime.now(timezone.utc)
    )

    db.commit()
    db.refresh(message)

    out = MessageOut.model_validate(
        message
    )

    await ws_manager.broadcast(
        conversation.id,
        out.model_dump(mode="json"),
    )

    return out


# ===========================================================================
# UPLOAD IMAGE MANAGER → CLOUDINARY
# ===========================================================================

@router.post(
    "/conversations/{conversation_id}/image"
)
async def upload_manager_chat_image(
    conversation_id: str,
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_manager: User = Depends(require_manager),
):

    mid = _acting_manager_id(
        request,
        current_manager,
        db,
    )

    _get_owned_conversation(
        db,
        conversation_id,
        mid,
    )

    image_url = _save_chat_image(file)

    return {
        "image_url": image_url
    }


# ===========================================================================
# CORBEILLE
# ===========================================================================

@router.post(
    "/conversations/{conversation_id}/trash"
)
def trash_conversation(
    conversation_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_manager: User = Depends(require_manager),
):

    mid = _acting_manager_id(
        request,
        current_manager,
        db,
    )

    conversation = _get_owned_conversation(
        db,
        conversation_id,
        mid,
    )

    conversation.trashed_at = (
        datetime.now(timezone.utc)
    )

    db.commit()

    return {
        "ok": True
    }


@router.post(
    "/conversations/{conversation_id}/restore"
)
def restore_conversation(
    conversation_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_manager: User = Depends(require_manager),
):

    mid = _acting_manager_id(
        request,
        current_manager,
        db,
    )

    conversation = _get_owned_conversation(
        db,
        conversation_id,
        mid,
    )

    conversation.trashed_at = None

    db.commit()

    return {
        "ok": True
    }


@router.delete(
    "/conversations/{conversation_id}",
    status_code=204,
)
def delete_conversation(
    conversation_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_manager: User = Depends(require_manager),
):

    mid = _acting_manager_id(
        request,
        current_manager,
        db,
    )

    conversation = _get_owned_conversation(
        db,
        conversation_id,
        mid,
    )

    db.delete(conversation)
    db.commit()

    return None


# ===========================================================================
# STATISTIQUES
# ===========================================================================

@router.get(
    "/stats/summary"
)
def unread_summary(
    request: Request,
    db: Session = Depends(get_db),
    current_manager: User = Depends(require_manager),
):

    mid = _acting_manager_id(
        request,
        current_manager,
        db,
    )

    total_unread = (
        db.query(func.count(Message.id))
        .join(
            Conversation,
            Message.conversation_id
            == Conversation.id,
        )
        .join(
            Artist,
            Conversation.artist_id
            == Artist.id,
        )
        .filter(
            Artist.manager_id == mid,
            Conversation.trashed_at.is_(None),
            Message.sender_type
            == SenderType.fan,
            Message.read_by_manager.is_(False),
        )
        .scalar()
    )

    return {
        "unread_messages": total_unread or 0
    }