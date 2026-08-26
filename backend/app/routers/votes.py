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


# ============================================================
# CLOUDINARY
# ============================================================

CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
UPLOAD_PRESET = os.getenv(
    "CLOUDINARY_UPLOAD_PRESET",
    "chatartist_uploads",
)

cloudinary.config(
    cloud_name=CLOUD_NAME,
    secure=True,
)


# ============================================================
# UPLOAD IMAGE
# ============================================================

ALLOWED = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
}

MAX_BYTES = 5 * 1024 * 1024


def _upload(file: UploadFile) -> str:
    if file.content_type not in ALLOWED:
        raise HTTPException(
            400,
            detail="Format image non supporté.",
        )

    data = file.file.read()

    if not data or len(data) > MAX_BYTES:
        raise HTTPException(
            400,
            detail="Image invalide ou trop lourde (max 5 Mo).",
        )

    try:
        result = cloudinary.uploader.unsigned_upload(
            data,
            UPLOAD_PRESET,
            folder="artistchat/votes",
            resource_type="image",
        )
    except Exception as exc:
        raise HTTPException(
            500,
            detail=f"Upload impossible : {str(exc)}",
        )

    url = result.get("secure_url")

    if not url:
        raise HTTPException(
            500,
            detail="Upload impossible.",
        )

    return url


# ============================================================
# ENVOI D'UNE PREUVE DE PAIEMENT
# ============================================================

@router.post(
    "/proof",
    response_model=VoteProofOut,
    status_code=201,
)
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
    """
    Fan connecté envoie une preuve de paiement.
    """

    if current_user.role != UserRole.fan:
        raise HTTPException(
            403,
            detail="Réservé aux fans.",
        )

    artist = (
        db.query(Artist)
        .filter(
            Artist.id == artist_id,
            Artist.is_published.is_(True),
        )
        .first()
    )

    if not artist:
        raise HTTPException(
            404,
            detail="Artiste introuvable.",
        )

    # --------------------------------------------------------
    # Upload de la preuve
    # --------------------------------------------------------

    proof_url = None

    if file is not None and file.filename:
        proof_url = _upload(file)

    # Pour les offres non VIP, une preuve est obligatoire.
    if tier != "vip" and not proof_url:
        raise HTTPException(
            400,
            detail="Photo / capture de paiement requise.",
        )

    # --------------------------------------------------------
    # Création de la preuve
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # VIP : ouvrir la conversation automatiquement
    # --------------------------------------------------------

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
            conv = Conversation(
                fan_id=current_user.id,
                artist_id=artist.id,
            )
            db.add(conv)
            db.flush()

        method_label = {
            "paypal": "PayPal",
            "postepay": "PostePay",
            "bank": "virement bancaire",
        }.get(
            payment_method,
            payment_method,
        )

        auto_text = (
            f"Demande de vote VIP : {votes} votes ({price_eur} €).\n\n"
            f"Mode de paiement choisi : {method_label}.\n\n"
            f"Un comptable vous enverra les coordonnées de paiement "
            f"pour effectuer le règlement. "
            f"Déposez ensuite la capture du paiement "
            f"dans cette conversation."
        )

        msg = Message(
            conversation_id=conv.id,
            sender_type=SenderType.manager,
            text=auto_text,
            read_by_manager=True,
        )

        db.add(msg)

        conv.updated_at = datetime.now(timezone.utc)
        conv.trashed_at = None

    # --------------------------------------------------------
    # Sauvegarde
    # --------------------------------------------------------

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


# ============================================================
# DÉMARRER UNE DEMANDE VIP
# ============================================================

@router.post("/start-vip")
async def start_vip_payment(
    artist_id: str = Form(...),
    votes: int = Form(...),
    price_eur: int = Form(...),
    payment_method: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Le fan sélectionne une offre VIP importante.

    Cette route :
    1. vérifie que l'utilisateur est un fan ;
    2. vérifie que l'artiste existe et est publié ;
    3. crée ou récupère la conversation fan ↔ artiste ;
    4. ajoute automatiquement un message ;
    5. crée une demande VoteProof avec le statut pending.

    Aucune image n'est nécessaire à cette étape.
    """

    # --------------------------------------------------------
    # Vérification du rôle
    # --------------------------------------------------------

    if current_user.role != UserRole.fan:
        raise HTTPException(
            status_code=403,
            detail="Réservé aux fans.",
        )

    # --------------------------------------------------------
    # Vérification de l'artiste
    # --------------------------------------------------------

    artist = (
        db.query(Artist)
        .filter(
            Artist.id == artist_id,
            Artist.is_published.is_(True),
        )
        .first()
    )

    if not artist:
        raise HTTPException(
            status_code=404,
            detail="Artiste introuvable.",
        )

    # --------------------------------------------------------
    # Libellé du moyen de paiement
    # --------------------------------------------------------

    method_label = {
        "paypal": "PayPal",
        "postepay": "PostePay",
        "bank": "virement bancaire",
    }.get(
        payment_method,
        payment_method,
    )

    # --------------------------------------------------------
    # Conversation fan ↔ artiste
    # --------------------------------------------------------

    conv = (
        db.query(Conversation)
        .filter(
            Conversation.fan_id == current_user.id,
            Conversation.artist_id == artist.id,
        )
        .first()
    )

    if not conv:
        conv = Conversation(
            fan_id=current_user.id,
            artist_id=artist.id,
        )

        db.add(conv)
        db.flush()

    # --------------------------------------------------------
    # Message automatique
    # --------------------------------------------------------

    auto_text = (
        f"Demande de vote VVIP : {votes} votes ({price_eur} €).\n"
        f"Mode de paiement choisi : {method_label}.\n\n"
        f"Le comptable va transmettre les coordonnées "
        f"nécessaires pour votre paiement.\n"
        f"Merci de patienter : vous recevrez les instructions "
        f"dans cette conversation, puis déposez la capture "
        f"une fois le paiement effectué."
    )

    msg = Message(
        conversation_id=conv.id,
        sender_type=SenderType.manager,
        text=auto_text,
        read_by_manager=False,
    )

    db.add(msg)

    # --------------------------------------------------------
    # Mise à jour de la conversation
    # --------------------------------------------------------

    conv.updated_at = datetime.now(timezone.utc)
    conv.trashed_at = None

    # --------------------------------------------------------
    # Création de la demande VIP
    # --------------------------------------------------------

    vp = VoteProof(
        artist_id=artist.id,
        fan_id=current_user.id,
        fan_email=current_user.email,
        fan_username=current_user.username,
        votes=votes,
        price_eur=price_eur,
        tier="vip",
        payment_method=payment_method,
        proof_image_url=None,
        status=VoteStatus.pending,
        note=f"Demande VIP ouverte — {method_label}",
    )

    db.add(vp)

    # --------------------------------------------------------
    # Sauvegarde
    # --------------------------------------------------------

    db.commit()
    db.refresh(conv)

    return {
        "ok": True,
        "conversation_id": conv.id,
        "artist_id": artist.id,
        "message": auto_text,
    }