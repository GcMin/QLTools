import json

import uvicorn
from fastapi import FastAPI, WebSocket, APIRouter
import logging
from net.MsgFilter import main_filter

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger("WS_logger")
logging.basicConfig(format=LOG_FORMAT)

router = APIRouter()


@router.websocket("/ws/qq")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_json()
        if "post_type" in data.keys() and data["post_type"] == "message":
            result = main_filter(data)
            for msg in result:
                if msg is not None:
                    await websocket.send_json(msg)
                else:
                    continue
        elif "meta_event_type" in data.keys() and data["meta_event_type"] == "heartbeat":
            continue
        else:
            test(data)


def test(data):
    logger.info(data)
