from fastapi import WebSocket
from typing import List, Dict
import json
import asyncio
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.message_queues: Dict[str, asyncio.Queue] = defaultdict(asyncio.Queue)

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.message_queues[id(websocket)] = asyncio.Queue()
        logger.info(f"Nueva conexión WebSocket. Total conexiones: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            self.message_queues.pop(id(websocket), None)
            logger.info(f"WebSocket desconectado. Conexiones restantes: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        logger.info(f"Intentando broadcast a {len(self.active_connections)} conexiones")
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
                logger.info(f"Mensaje enviado exitosamente a una conexión")
            except Exception as e:
                logger.error(f"Error en broadcast: {e}")
                disconnected.append(connection)
        
        # Limpiar conexiones desconectadas
        for conn in disconnected:
            await self.disconnect(conn)

    async def receive_warnings(self, timeout: int = 5):
        warnings = []
        logger.info("Esperando warnings...")
        
        try:
            end_time = asyncio.get_event_loop().time() + timeout
            
            while asyncio.get_event_loop().time() < end_time:
                for connection in self.active_connections:
                    try:
                        # Usar un timeout corto para cada intento de recepción
                        message = await asyncio.wait_for(
                            connection.receive_json(),
                            timeout=0.1
                        )
                        
                        logger.info(f"Mensaje recibido: {message}")
                        
                        if message.get("type") == "warning":
                            warnings.append(message["message"])
                            return warnings  # Retornar inmediatamente si hay warning
                            
                    except asyncio.TimeoutError:
                        continue
                    except Exception as e:
                        logger.error(f"Error recibiendo mensaje: {e}")
                        continue
                
                await asyncio.sleep(0.1)  # Pequeña pausa entre ciclos
                
        except Exception as e:
            logger.error(f"Error en receive_warnings: {e}")
        
        return warnings

ws_manager = WebSocketManager() 