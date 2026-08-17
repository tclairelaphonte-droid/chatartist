from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:
    """
    Registre en mémoire des sockets ouverts par conversation.
    Suffisant pour un seul process ; pour scaler sur plusieurs workers,
    remplacer par un pub/sub Redis (mêmes points d'entrée).
    """

    def __init__(self):
        self.active: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(self, conversation_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active[conversation_id].append(websocket)

    def disconnect(self, conversation_id: str, websocket: WebSocket):
        if websocket in self.active[conversation_id]:
            self.active[conversation_id].remove(websocket)
        if not self.active[conversation_id]:
            self.active.pop(conversation_id, None)

    async def broadcast(self, conversation_id: str, payload: dict):
        for ws in list(self.active.get(conversation_id, [])):
            try:
                await ws.send_json(payload)
            except Exception:
                self.disconnect(conversation_id, ws)


manager = ConnectionManager()
