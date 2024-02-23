from fastapi import APIRouter, WebSocket, WebSocketDisconnect, WebSocketException, status

router = APIRouter(
    prefix="/websocket",
    tags=["websocket"]
)


class ConnectionManager:
    def __init__(self):
        self.client = None
        self.source_channel = None
        self.target_channel = None

    async def connect(self, websocket: WebSocket, username: str):
        await websocket.accept()

    async def disconnect(self, websocket: WebSocket):
        await websocket.close()


@router.websocket("/ws/connect/{username}")
async def websocket_parsing(websocket: WebSocket, username: str | int):
    raise WebSocketException(code=status.WsErrorCode.NOT_FOUND)
