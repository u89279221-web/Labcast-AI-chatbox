import asyncio
import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import List
from jose import jwt, JWTError
import paho.mqtt.client as mqtt

from app.core.config import settings
from app.core.deps import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ws",
    tags=["websocket"]
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket, token: str):
        # Validate token
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            user_id: str = payload.get("sub")
            if user_id is None:
                await websocket.close(code=1008)
                return False
        except JWTError:
            await websocket.close(code=1008)
            return False
            
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total: {len(self.active_connections)}")
        return True

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")

    async def broadcast_json(self, message: dict):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Error sending WS message: {e}")
                self.disconnect(connection)

manager = ConnectionManager()

# Global event loop reference for the MQTT thread to push back to asyncio
main_loop = None

def on_mqtt_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("WebSocket MQTT Bridge connected to broker")
        # Subscribe to relevant topics
        client.subscribe("labcast/#")
    else:
        logger.warning(f"WebSocket MQTT Bridge failed to connect, return code {rc}")

def on_mqtt_message(client, userdata, msg):
    try:
        payload_str = msg.payload.decode('utf-8')
        payload = json.loads(payload_str)
        # Format the event for the frontend
        event = {
            "topic": msg.topic,
            "payload": payload
        }
        
        if main_loop and manager.active_connections:
            # Safely schedule the broadcast on the main asyncio loop
            asyncio.run_coroutine_threadsafe(manager.broadcast_json(event), main_loop)
            
    except Exception as e:
        logger.error(f"Error processing MQTT message for WS broadcast: {e}")

# We will initialize this only once
mqtt_client = None

def start_mqtt_bridge(loop):
    global main_loop, mqtt_client
    main_loop = loop
    
    if not settings.mqtt_broker_host:
        logger.warning("No MQTT broker host configured, skipping WebSocket MQTT Bridge")
        return
        
    try:
        mqtt_client = mqtt.Client(client_id="labcast_backend_ws_bridge")
        if settings.mqtt_username:
            mqtt_client.username_pw_set(settings.mqtt_username, settings.mqtt_password or "")
            
        mqtt_client.on_connect = on_mqtt_connect
        mqtt_client.on_message = on_mqtt_message
        
        mqtt_client.connect(settings.mqtt_broker_host, settings.mqtt_broker_port, 60)
        # Start background network loop
        mqtt_client.loop_start()
        logger.info("WebSocket MQTT Bridge started")
    except Exception as e:
        logger.error(f"Failed to start WebSocket MQTT Bridge: {e}")

@router.websocket("/events")
async def websocket_endpoint(websocket: WebSocket, token: str):
    is_valid = await manager.connect(websocket, token)
    if not is_valid:
        return
        
    try:
        while True:
            # We don't expect the client to send much, but we must receive to detect disconnects
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
