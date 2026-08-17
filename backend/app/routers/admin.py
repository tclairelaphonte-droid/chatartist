from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_admin
from app.models import Artist, User, UserRole
from app.schemas import ManagerAdminOut, ArtistOut

router = APIRouter(prefix="/admin", tags=["admin"])


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
    _admin: User = Depends(require_admin),
):
    """Rétablit l'accès du manager."""
    manager = (
        db.query(User)
        .filter(User.id == manager_id, User.role == UserRole.manager)
        .first()
    )
    if not manager:
        raise HTTPException(status_code=404, detail="Manager introuvable.")

    manager.is_blocked = False
    db.commit()
    return {"ok": True, "id": manager.id, "is_blocked": False}