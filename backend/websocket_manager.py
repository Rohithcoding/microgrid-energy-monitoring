from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict, Any
import json
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Manages WebSocket connections for real-time data streaming"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_info: Dict[WebSocket, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, client_info: Dict[str, Any] = None):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_info[websocket] = client_info or {}
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            if websocket in self.connection_info:
                del self.connection_info[websocket]
            logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket connection"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: str):
        """Broadcast a message to all connected WebSocket clients"""
        if not self.active_connections:
            return
        
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
    
    async def broadcast_json(self, data: Dict[str, Any]):
        """Broadcast JSON data to all connected clients"""
        message = json.dumps(data, default=str)
        await self.broadcast(message)
    
    async def send_sensor_data(self, sensor_data: Dict[str, Any]):
        """Send sensor data to all connected clients"""
        message = {
            "type": "sensor_data",
            "data": sensor_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast_json(message)
    
    async def send_alert(self, alert_data: Dict[str, Any]):
        """Send alert data to all connected clients"""
        message = {
            "type": "alert",
            "data": alert_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast_json(message)
    
    async def send_system_status(self, status_data: Dict[str, Any]):
        """Send system status to all connected clients"""
        message = {
            "type": "system_status",
            "data": status_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast_json(message)
    
    def get_connection_count(self) -> int:
        """Get the number of active connections"""
        return len(self.active_connections)
    
    def get_connection_info(self) -> List[Dict[str, Any]]:
        """Get information about all active connections"""
        return list(self.connection_info.values())

# Global WebSocket manager instance
websocket_manager = WebSocketManager()

class WebSocketHandler:
    """Handles WebSocket message processing"""
    
    def __init__(self, manager: WebSocketManager):
        self.manager = manager
    
    async def handle_connection(self, websocket: WebSocket, client_id: str = None):
        """Handle a new WebSocket connection"""
        client_info = {
            "client_id": client_id,
            "connected_at": datetime.utcnow(),
            "message_count": 0
        }
        
        await self.manager.connect(websocket, client_info)
        
        try:
            # Send welcome message
            welcome_message = {
                "type": "connection",
                "message": "Connected to Microgrid WebSocket",
                "client_id": client_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            await websocket.send_text(json.dumps(welcome_message, default=str))
            
            # Keep connection alive and handle incoming messages
            while True:
                try:
                    # Wait for messages from client
                    data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                    await self.process_message(websocket, data)
                except asyncio.TimeoutError:
                    # Send ping to keep connection alive
                    ping_message = {
                        "type": "ping",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    await websocket.send_text(json.dumps(ping_message, default=str))
                
        except WebSocketDisconnect:
            logger.info(f"WebSocket client {client_id} disconnected")
        except Exception as e:
            logger.error(f"WebSocket error for client {client_id}: {e}")
        finally:
            self.manager.disconnect(websocket)
    
    async def process_message(self, websocket: WebSocket, message: str):
        """Process incoming WebSocket messages"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "pong":
                # Handle pong response
                pass
            elif message_type == "subscribe":
                # Handle subscription requests
                await self.handle_subscription(websocket, data)
            elif message_type == "unsubscribe":
                # Handle unsubscription requests
                await self.handle_unsubscription(websocket, data)
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON received from WebSocket client")
        except Exception as e:
            logger.error(f"Error processing WebSocket message: {e}")
    
    async def handle_subscription(self, websocket: WebSocket, data: Dict[str, Any]):
        """Handle subscription requests"""
        # Update connection info with subscription preferences
        if websocket in self.manager.connection_info:
            self.manager.connection_info[websocket]["subscriptions"] = data.get("topics", [])
        
        response = {
            "type": "subscription_confirmed",
            "topics": data.get("topics", []),
            "timestamp": datetime.utcnow().isoformat()
        }
        await websocket.send_text(json.dumps(response, default=str))
    
    async def handle_unsubscription(self, websocket: WebSocket, data: Dict[str, Any]):
        """Handle unsubscription requests"""
        # Update connection info to remove subscriptions
        if websocket in self.manager.connection_info:
            current_subs = self.manager.connection_info[websocket].get("subscriptions", [])
            topics_to_remove = data.get("topics", [])
            updated_subs = [topic for topic in current_subs if topic not in topics_to_remove]
            self.manager.connection_info[websocket]["subscriptions"] = updated_subs
        
        response = {
            "type": "unsubscription_confirmed",
            "topics": data.get("topics", []),
            "timestamp": datetime.utcnow().isoformat()
        }
        await websocket.send_text(json.dumps(response, default=str))

# Global WebSocket handler instance
websocket_handler = WebSocketHandler(websocket_manager)
