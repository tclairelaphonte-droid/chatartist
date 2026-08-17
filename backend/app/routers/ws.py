from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Conversation, User
from app.security import decode_access_token
from app.ws_manager import manager as ws_manager

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/conversations/{conversation_id}")
async def conversation_socket(websocket: WebSocket, conversation_id: str, token: str = Query(...)):
    """
    Connexion en temps réel pour un fil de discussion précis.
    Le front (fan ou manager) ouvre ce socket après avoir chargé l'historique
    via l'API REST, et reçoit ensuite chaque nouveau message poussé ici.
    Utilisé par fan-messages.html et manager-dashboard.html.
    """
    payload = decode_access_token(token)
    if payload is None:
        await websocket.close(code=4401)
        return

    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.id == payload.get("sub")).first()
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()

        if not user or not conversation:
            await websocket.close(code=4404)
            return

        is_owner_fan = user.role.value == "fan" and conversation.fan_id == user.id
        is_manager = user.role.value == "manager"
        if not (is_owner_fan or is_manager):
            await websocket.close(code=4403)
            return
    finally:
        db.close()

    await ws_manager.connect(conversation_id, websocket)
    try:
        while True:
            # On ne traite pas de messages entrants ici : l'envoi passe par
            # l'API REST (POST /conversations/{id}/messages), qui se charge
            # de la persistance puis rebroadcast sur ce socket.
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(conversation_id, websocket)
