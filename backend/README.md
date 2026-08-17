# Backstage API

API FastAPI + PostgreSQL pour la plateforme communautaire (fans ↔ management, 3 artistes,
messagerie temps réel, photos, dashboard manager).

## Installation

```bash
python -m venv .venv
source .venv/bin/activate          # Windows : .venv\Scripts\activate
pip install -r requirements.txt
```

## Base de données

1. Créer une base PostgreSQL et un utilisateur :

```sql
CREATE DATABASE backstage;
CREATE USER backstage_user WITH PASSWORD 'backstage_pw';
GRANT ALL PRIVILEGES ON DATABASE backstage TO backstage_user;
```

2. Copier `.env.example` en `.env` et ajuster `BACKSTAGE_DATABASE_URL` si besoin.

3. Créer les tables + les 3 artistes + le compte manager :

```bash
python -m app.seed
```

Cela affiche les identifiants du compte manager de démonstration
(`manager@backstage-studio.com` / `change-moi`) — **à changer immédiatement**
en production (voir plus bas).

## Lancer le serveur

```bash
uvicorn app.main:app --reload --port 8000
```

- Documentation interactive : http://localhost:8000/docs
- Santé du service : http://localhost:8000/health

## Comment ça correspond au frontend

| Page frontend              | Endpoints utilisés |
|-----------------------------|---------------------|
| `index.html`                 | `GET /artists` |
| `artist.html`                 | `GET /artists/{id}` |
| `login.html`                   | `POST /auth/register`, `POST /auth/login` |
| `fan-messages.html`             | `POST /conversations/start/{artist_id}`, `GET/POST /conversations/{id}/messages`, `POST /uploads/image`, `WS /ws/conversations/{id}` |
| `manager-dashboard.html`         | `GET /artists` (compteurs), `GET /manager/artists/{id}/conversations`, `GET/POST /manager/conversations/{id}/messages`, `POST /uploads/image`, `WS /ws/conversations/{id}` |

Le bouton **« Discuter avec le management »** appelle `POST /conversations/start/{artist_id}`
avec l'ID de l'artiste pris dans l'URL de la page — le fan n'a jamais besoin de le
sélectionner lui-même, exactement comme demandé dans le cahier des charges.

## Authentification

- JWT porté dans l'en-tête `Authorization: Bearer <token>`.
- Un seul rôle `manager` (compte unique pour vous, pas un compte par artiste).
- Les routes `/manager/*` sont protégées et renvoient `403` pour un compte fan.

## Photos dans la messagerie

1. Le client envoie le fichier via `POST /uploads/image` (multipart, jpg/png/webp/gif,
   5 Mo max par défaut) → reçoit une URL.
2. Cette URL est envoyée dans `image_url` du `POST .../messages`.
3. Le message est aussitôt repoussé aux deux parties via le WebSocket de la conversation.

En production, remplacer le stockage disque (`uploads/`) par un stockage objet
(S3, GCS, Object Storage…) derrière un CDN, et faire encoder/redimensionner les
images à l'upload pour éviter de servir des fichiers trop lourds.

## Notes de production

- Remplacer `Base.metadata.create_all()` par des migrations **Alembic** versionnées.
- Changer `BACKSTAGE_JWT_SECRET` et le mot de passe manager par défaut.
- Restreindre `cors_origins` au(x) vrai(s) domaine(s) du frontend.
- `ConnectionManager` (WebSocket) est en mémoire — suffisant pour un seul
  process ; passer par un pub/sub (Redis) pour scaler sur plusieurs workers.
