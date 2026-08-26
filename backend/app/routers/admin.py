from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_admin
from app.models import Artist, User, UserRole
from app.schemas import ManagerAdminOut, ArtistOut

router = APIRouter(prefix="/admin", tags=["admin"])


class FanEmailOut(BaseModel):
    id: str
    email: EmailStr
    username: str
    created_at: Optional[datetime] = None
    is_blocked: bool = False

    class Config:
        from_attributes = True


class FanIdsIn(BaseModel):
    ids: list[str]


@router.get("/fans", response_model=list[FanEmailOut])
def list_fans(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    """Tous les comptes fan (emails) — admin uniquement."""
    fans = (
        db.query(User)
        .filter(User.role == UserRole.fan)
        .order_by(User.created_at.desc())
        .all()
    )
    return [
        FanEmailOut(
            id=f.id,
            email=f.email,
            username=f.username,
            created_at=f.created_at,
            is_blocked=bool(getattr(f, "is_blocked", False)),
        )
        for f in fans
    ]


@router.delete("/fans/{fan_id}")
def delete_fan(
    fan_id: str,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    """Supprime un compte fan."""
    fan = (
        db.query(User)
        .filter(User.id == fan_id, User.role == UserRole.fan)
        .first()
    )
    if not fan:
        raise HTTPException(status_code=404, detail="Fan introuvable.")

    db.delete(fan)
    db.commit()
    return {"ok": True, "id": fan_id}


@router.post("/fans/delete-many")
def delete_fans_many(
    payload: FanIdsIn,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    """Supprime plusieurs fans. Body: { \"ids\": [\"...\"] }"""
    if not payload.ids:
        raise HTTPException(status_code=400, detail="Liste d'ids vide.")

    deleted = 0
    for fan_id in payload.ids:
        fan = (
            db.query(User)
            .filter(User.id == fan_id, User.role == UserRole.fan)
            .first()
        )
        if fan:
            db.delete(fan)
            deleted += 1

    db.commit()
    return {"ok": True, "deleted": deleted}


@router.get("/managers", response_model=list[ManagerAdminOut])
def list_managers(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    """Tous les managers clients (pas les fans, pas les autres admins)."""
    managers = (
        db.query(User)
        .filter(User.role == UserRole.manager)
        .order_by(User.created_at.desc())
        .all()
    )
    results = []
    for m in managers:
        count = (
            db.query(func.count(Artist.id))
            .filter(Artist.manager_id == m.id)
            .scalar()
        ) or 0
        results.append(
            ManagerAdminOut(
                id=m.id,
                username=m.username,
                email=m.email,
                is_blocked=bool(getattr(m, "is_blocked", False)),
                created_at=m.created_at,
                artist_count=count,
            )
        )
    return results


@router.get("/managers/{manager_id}/artists", response_model=list[ArtistOut])
def manager_artists(
    manager_id: str,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    """Artistes d'un manager (supervision)."""
    manager = (
        db.query(User)
        .filter(User.id == manager_id, User.role == UserRole.manager)
        .first()
    )
    if not manager:
        raise HTTPException(status_code=404, detail="Manager introuvable.")
    return (
        db.query(Artist)
        .filter(Artist.manager_id == manager.id)
        .order_by(Artist.name.asc())
        .all()
    )


@router.post("/managers/{manager_id}/block")
def block_manager(
    manager_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Suspend le compte manager (plus de login)."""
    if manager_id == admin.id:
        raise HTTPException(status_code=400, detail="Impossible de vous bloquer vous-même.")

    manager = (
        db.query(User)
        .filter(User.id == manager_id, User.role == UserRole.manager)
        .first()
    )
    if not manager:
        raise HTTPException(status_code=404, detail="Manager introuvable.")

    manager.is_blocked = True
    db.commit()
    return {"ok": True, "id": manager.id, "is_blocked": True}


@router.post("/managers/{manager_id}/unblock")
def unblock_manager(
    manager_id: str,
    db: Session = Depends(get_db),
