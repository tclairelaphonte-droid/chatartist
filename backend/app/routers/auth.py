from datetime import datetime, timedelta, timezone
import secrets
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import User, UserRole
from app.schemas import (
    RegisterIn, LoginIn, TokenOut, MeOut,
    ForgotPasswordIn, ForgotPasswordOut, ResetPasswordIn,
)
from app.security import hash_password, verify_password, create_access_token
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

RESET_TOKEN_VALID_MINUTES = 30

ALLOWED_AVATAR_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}
MAX_AVATAR_BYTES = 3 * 1024 * 1024  # 3 Mo


@router.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    """Inscription fan uniquement."""
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Cette adresse e-mail est déjà utilisée.")
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="Ce nom d'utilisateur est déjà pris.")

    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=UserRole.fan,
        is_blocked=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(subject=user.id, role=user.role.value)
    return TokenOut(access_token=token)


@router.post("/register-manager", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
def register_manager(payload: RegisterIn, db: Session = Depends(get_db)):
    """Inscription d'un nouveau manager (multi-tenant)."""
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Cette adresse e-mail est déjà utilisée.")
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="Ce nom d'utilisateur est déjà pris.")

    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=UserRole.manager,
        is_blocked=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(subject=user.id, role=user.role.value)
    return TokenOut(access_token=token)


@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="E-mail ou mot de passe incorrect.")

    # Compte suspendu par l'admin plateforme
    if getattr(user, "is_blocked", False):
        raise HTTPException(
            status_code=403,
            detail="Compte suspendu. Contactez le support Backstage.",
        )

    token = create_access_token(subject=user.id, role=user.role.value)
    return TokenOut(access_token=token)


@router.get("/me", response_model=MeOut)
def me(current_user: User = Depends(get_current_user)):
    if getattr(current_user, "is_blocked", False):
        raise HTTPException(
            status_code=403,
            detail="Compte suspendu. Contactez le support Backstage.",
        )
    return current_user


@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload de la photo de profil.
    - Enregistre le fichier dans /files/avatars/
    - Met à jour User.avatar_url
    - Retourne {"avatar_url": "..."}
    """
    if file.content_type not in ALLOWED_AVATAR_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Format non supporté. Utilisez JPEG, PNG ou WebP.",
        )

    data = await file.read()
    if len(data) > MAX_AVATAR_BYTES:
        raise HTTPException(
            status_code=400,
            detail="Image trop lourde (max 3 Mo).",
        )

    ext = ALLOWED_AVATAR_TYPES[file.content_type]
    folder = Path(settings.upload_dir) / "avatars"
    folder.mkdir(parents=True, exist_ok=True)

    filename = f"{current_user.id}_{uuid.uuid4().hex}{ext}"
    filepath = folder / filename
    filepath.write_bytes(data)

    avatar_url = f"/files/avatars/{filename}"

    current_user.avatar_url = avatar_url
    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return {"avatar_url": avatar_url}


@router.post("/forgot-password", response_model=ForgotPasswordOut)
def forgot_password(payload: ForgotPasswordIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    generic_message = (
        "Si un compte existe avec cette adresse, un lien de réinitialisation a été envoyé."
    )

    if not user:
        return ForgotPasswordOut(message=generic_message)

    token = secrets.token_urlsafe(32)
    user.reset_token = token
    user.reset_token_expires = datetime.now(timezone.utc) + timedelta(
        minutes=RESET_TOKEN_VALID_MINUTES
    )
    db.commit()

    return ForgotPasswordOut(message=generic_message, dev_reset_token=token)


@router.post("/reset-password")
def reset_password(payload: ResetPasswordIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.reset_token == payload.token).first()
    if not user or not user.reset_token_expires:
        raise HTTPException(status_code=400, detail="Lien de réinitialisation invalide.")

    expires = user.reset_token_expires
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if expires < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Ce lien de réinitialisation a expiré.")

    user.password_hash = hash_password(payload.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()

    return {"message": "Mot de passe mis à jour. Vous pouvez vous connecter."}