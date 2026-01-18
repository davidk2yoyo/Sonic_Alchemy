"""
WebSocket endpoint for real-time collaboration.
"""
from fastapi import WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Set
import json
import logging
from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.models.project import Project

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and project rooms."""
    
    def __init__(self):
        """Initialize connection manager."""
        # project_id -> Set[WebSocket]
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # WebSocket -> user_id
        self.connection_users: Dict[WebSocket, int] = {}
        # WebSocket -> project_id
        self.connection_projects: Dict[WebSocket, int] = {}
    
    async def connect(self, websocket: WebSocket, project_id: int, user_id: int):
        """Connect a user to a project room."""
        await websocket.accept()
        
        if project_id not in self.active_connections:
            self.active_connections[project_id] = set()
        
        self.active_connections[project_id].add(websocket)
        self.connection_users[websocket] = user_id
        self.connection_projects[websocket] = project_id
        
        # Notify others in the room
        await self.broadcast_to_project(
            project_id,
            {
                "type": "user_joined",
                "user_id": user_id,
                "project_id": project_id
            },
            exclude=websocket
        )
        
        logger.info(f"User {user_id} joined project {project_id}")
    
    def disconnect(self, websocket: WebSocket):
        """Disconnect a user from a project room."""
        if websocket not in self.connection_projects:
            return
        
        project_id = self.connection_projects[websocket]
        user_id = self.connection_users.get(websocket)
        
        if project_id in self.active_connections:
            self.active_connections[project_id].discard(websocket)
            if not self.active_connections[project_id]:
                del self.active_connections[project_id]
        
        self.connection_users.pop(websocket, None)
        self.connection_projects.pop(websocket, None)
        
        # Notify others in the room
        if project_id in self.active_connections:
            self.broadcast_to_project_sync(
                project_id,
                {
                    "type": "user_left",
                    "user_id": user_id,
                    "project_id": project_id
                }
            )
        
        logger.info(f"User {user_id} left project {project_id}")
    
    async def broadcast_to_project(
        self,
        project_id: int,
        message: dict,
        exclude: WebSocket = None
    ):
        """Broadcast message to all connections in a project."""
        if project_id not in self.active_connections:
            return
        
        disconnected = []
        for connection in self.active_connections[project_id]:
            if connection == exclude:
                continue
            
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for conn in disconnected:
            self.disconnect(conn)
    
    def broadcast_to_project_sync(
        self,
        project_id: int,
        message: dict
    ):
        """Synchronous broadcast (for use in disconnect)."""
        if project_id not in self.active_connections:
            return
        
        import asyncio
        asyncio.create_task(
            self.broadcast_to_project(project_id, message)
        )
    
    async def send_personal_message(self, websocket: WebSocket, message: dict):
        """Send message to a specific connection."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)


# Global connection manager
manager = ConnectionManager()


async def websocket_endpoint(
    websocket: WebSocket,
    project_id: int,
    token: str,
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for project collaboration.
    
    Args:
        websocket: WebSocket connection
        project_id: Project ID to join
        token: JWT authentication token
        db: Database session
    """
    # Verify user authentication
    from app.core.security import decode_token
    
    payload = decode_token(token)
    if not payload:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    user_id = int(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    # Verify project exists and user has access
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    if project.user_id != user_id and not project.is_public:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    # Connect to project room
    await manager.connect(websocket, project_id, user_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                message_type = message.get("type")
                
                if message_type == "ping":
                    # Respond to ping
                    await manager.send_personal_message(
                        websocket,
                        {"type": "pong"}
                    )
                
                elif message_type == "project_update":
                    # Broadcast project update to all users in room
                    await manager.broadcast_to_project(
                        project_id,
                        {
                            "type": "project_update",
                            "user_id": user_id,
                            "data": message.get("data", {})
                        },
                        exclude=websocket
                    )
                
                elif message_type == "task_complete":
                    # Notify about task completion
                    await manager.broadcast_to_project(
                        project_id,
                        {
                            "type": "task_complete",
                            "task_id": message.get("task_id"),
                            "task_type": message.get("task_type"),
                            "result": message.get("result", {})
                        }
                    )
                
                else:
                    logger.warning(f"Unknown message type: {message_type}")
            
            except json.JSONDecodeError:
                logger.error("Invalid JSON received")
                await manager.send_personal_message(
                    websocket,
                    {"type": "error", "message": "Invalid JSON"}
                )
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"WebSocket disconnected for user {user_id}")
