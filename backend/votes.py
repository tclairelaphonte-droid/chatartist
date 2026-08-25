import os
from datetime import datetime, timezone

import cloudinary
import cloudinary.uploader

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import (
    Artist,
    Conversation,
    Message,
    SenderType,
    User,
    UserRole,
    VoteProof,
    VoteStatus,
)
from app.schemas import VoteProofOut

router = APIRouter(prefix="/votes", tags=["votes"])


CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
UPLOAD_PRESET = os.getenv("CLOUDINARY_UPLOAD_PRESET", "chatartist_uploads")
cloudinary.config(cloud_name=CLOUD_NAME, secure=True)


ALLOWED = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_BYTES = 5 * 1024 * 1024



def _upload(file: UploadFile) -> str:
    if file.content_type not in ALLOWED:
        raise HTTPException(400, detail="Format image non supporté.")
    data = file.file.read()
    if not data or len(data) > MAX_BYTES:
        raise HTTPException(400, detail="Image invalide ou trop lourde (max 5 Mo).")
    result = cloudinary.uploader.unsigned_upload(
        data,
        UPLOAD_PRESET,
        folder="artistchat/votes",
        resource_type="image",
    )
    url = result.get("secure_url")
    if not url:
        raise HTTPException(500, detail="Upload impossible.")
    return url




@router.post("/proof", response_model=VoteProofOut, status_code=201)
async def submit_vote_proof(
    artist_id: str = Form(...),
    votes: int = Form(...),
    price_eur: int = Form(...),
    tier: str = Form("small"),
    payment_method: str = Form(...),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fan connecté (email) envoie une preuve de paiement."""

    if current_user.role != UserRole.fan:
        raise HTTPException(403, detail="Réservé aux fans.")

    artist = (
        db.query(Artist)
        .filter(
            Artist.id == artist_id,
            Artist.is_published.is_(True),
        )
        .first()
    )
    if not artist:
        raise HTTPException(404, detail="Artiste introuvable.")

    proof_url = None
    if file is not None and file.filename:
        proof_url = _upload(file)

    # Gros montants sans image encore autorisés (RIB en conversation)
    if tier != "vip" and not proof_url:
        raise HTTPException(400, detail="Photo / capture de paiement requise.")

    vp = VoteProof(
        artist_id=artist.id,
        fan_id=current_user.id,
        fan_email=current_user.email,
        fan_username=current_user.username,
        votes=votes,
        price_eur=price_eur,
        tier=tier if tier in ("small", "vip") else "small",
        payment_method=payment_method,
        proof_image_url=proof_url,
        status=VoteStatus.pending,
    )
    db.add(vp)

    # VIP : ouvrir / mettre à jour la conversation + message auto RIB
    if tier == "vip":
        conv = (
            db.query(Conversation)
            .filter(
                Conversation.fan_id == current_user.id,
                Conversation.artist_id == artist.id,
            )
            .first()
        )
        if not conv:
            conv = Conversation(fan_id=current_user.id, artist_id=artist.id)
            db.add(conv)
            db.flush()

        method_label = {
            "paypal": "PayPal",
            "postepay": "PostePay",
            "bank": "virement bancaire",
        }.get(payment_method, payment_method)

        auto_text = (
            f"Demande de vote VIP : {votes} votes ({price_eur} €). "
            f"Mode de paiement choisi : {method_label}. "
            f"Un comptable vous enverra le RIB du compte pour effectuer le paiement. "
            f"Déposez ensuite la capture dans cette conversation."
        )
        msg = Message(
            conversation_id=conv.id,
            sender_type=SenderType.manager,
            text=auto_text,
            read_by_manager=True,
        )
        db.add(msg)
        conv.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(vp)

    return VoteProofOut(
        id=vp.id,
        artist_id=vp.artist_id,
        artist_name=artist.name,
        fan_id=vp.fan_id,
        fan_email=vp.fan_email,
        fan_username=vp.fan_username,
        votes=vp.votes,
        price_eur=vp.price_eur,
        tier=vp.tier,
        payment_method=vp.payment_method,
        proof_image_url=vp.proof_image_url,
        status=vp.status.value,
        note=vp.note,
        created_at=vp.created_at,
    )