"""
Initialise les données de base :
- 1 compte admin = manager@backstage.com (toi + 3 artistes)
- 5 comptes managers clients
Usage : python -m app.seed
"""
from app.database import SessionLocal, engine, Base
from app.models import Artist, User, UserRole
from app.security import hash_password

ARTISTS = [
    dict(
        slug="bruce-springsteen",
        name="Bruce Springsteen",
        genre="Rock · Heartland rock · Folk rock · Americana",
        bio_short="Voix chaude, productions minimalistes.",
        bio_full=(
            "Bruce Springsteen naît le 23 septembre 1949 à Long Branch, "
            "dans l'État du New Jersey, aux États-Unis."
        ),
        avatar_url="assets/artiste1/avatar.jpg",
        cover_url="assets/artiste1/cover.jpg",
        is_published=True,
    ),
    dict(
        slug="annalisa-scarrone",
        name="Annalisa Scarrone",
        genre="Synth-pop · Dance-pop · Electropop · Pop",
        bio_short="Figure incontournable du Festival de Sanremo.",
        bio_full=(
            "Annalisa Scarrone est une chanteuse italienne née le 5 août 1985 "
            "à Savone, en Ligurie."
        ),
        avatar_url="assets/artiste1/avatar1.jpg",
        cover_url="assets/artiste1/cover4.jpg",
        is_published=True,
    ),
    dict(
        slug="shania-twain",
        name="Shania Twain",
        genre="Country · Pop · Rock · Soft Rock",
        bio_short="Reine de la Country Pop.",
        bio_full=(
            "Shania Twain, de son vrai nom Eilleen Regina Edwards, "
            "est une chanteuse canadienne née le 28 août 1965."
        ),
        avatar_url="assets/artiste1/avatar5.jpg",
        cover_url="assets/artiste1/cover5.jpg",
        is_published=True,
    ),
]
CLIENT_MANAGERS = [
    ("manager1", "manager1@backstage.com", "c_lient1@2021+"),
    ("manager2", "manager2@backstage.com", "Manager@2@22!"),
    ("manager3", "manager3@backstage.com", "Client3&2@23!"),
    ("manager4", "manager4@backstage.com", "backstage4@2024+"),
    ("manager5", "manager5@backstage.com", "M@nager+5@2026!"),
]


def _upsert_user(db, username, email, password, role):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = db.query(User).filter(User.username == username).first()
    if user:
        user.username = username
        user.email = email
        user.password_hash = hash_password(password)
        user.role = role
        user.is_blocked = False
        print("Mis à jour:", email, "→", role.value)
    else:
        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            role=role,
            is_blocked=False,
        )
        db.add(user)
        print("Créé:", email, "→", role.value)
    return user


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # TOI = admin plateforme + propriétaire des 3 artistes
        owner = _upsert_user(
            db,
            username="manager",
            email="manager@backstage.com",
            password="man@g&r1972",
            role=UserRole.admin,
        )

        db.flush()

        # 5 managers clients (à attribuer / vendre)
        for username, email, password in CLIENT_MANAGERS:
            _upsert_user(db, username, email, password, UserRole.manager)

        db.flush()

        OLD_SLUGS = ["alya-voss", "kesh", "noane"]
        deleted = (
            db.query(Artist)
            .filter(Artist.slug.in_(OLD_SLUGS))
            .delete(synchronize_session=False)
        )
        print("Anciens artistes supprimés:", deleted)

        for data in ARTISTS:
            payload = dict(data)
            payload["manager_id"] = owner.id
            payload["is_published"] = payload.get("is_published", True)

            existing = db.query(Artist).filter(Artist.slug == payload["slug"]).first()
            if not existing:
                db.add(Artist(**payload))
                print("Créé artiste:", payload["name"])
            else:
                for key, value in payload.items():
                    setattr(existing, key, value)
                print("Mis à jour artiste:", payload["name"])

        orphans = db.query(Artist).filter(Artist.manager_id.is_(None)).all()
        for a in orphans:
            a.manager_id = owner.id
            print("Rattaché (orphelin):", a.name)

        db.commit()

        n_admin = db.query(User).filter(User.role == UserRole.admin).count()
        n_managers = db.query(User).filter(User.role == UserRole.manager).count()
        n_art = db.query(Artist).filter(Artist.manager_id == owner.id).count()
        print("Admins:", n_admin, "| Managers clients:", n_managers)
        print("Artistes de manager@backstage.com:", n_art)
        print("Seed terminé.")
        print("Admin: manager@backstage.com / man@g&r1972")

    finally:
        db.close()


if __name__ == "__main__":
    run()