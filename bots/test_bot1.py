import asyncio
import websockets
import json
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def monitor_transactions():
    uri = "ws://localhost:8000/ws/bot"
    
    while True:  # Bucle principal para reconexión
        try:
            async with websockets.connect(uri) as websocket:
                logger.info("✅ Bot conectado al servidor")
                
                while True:
                    try:
                        # Recibir mensaje
                        message = await websocket.recv()
                        logger.info(f"📩 Mensaje recibido: {message}")
                        
                        data = json.loads(message)
                        
                        if data.get("type") == "transaction":
                            transaction = data.get("data", {})
                            logger.info(f"🔍 Analizando transacción: {transaction}")
                            
                            # Verificar si la palabra "oso" está en la transacción
                            transaction_str = json.dumps(transaction).lower()
                            if "oso" in transaction_str:
                                warning = {
                                    "type": "warning",
                                    "message": "peludo",
                                    "transaction_hash": transaction.get("hash"),
                                    "timestamp": datetime.utcnow().isoformat()
                                }
                                
                                # Enviar warning
                                await websocket.send(json.dumps(warning))
                                logger.info(f"⚠️ Warning enviado: {warning}")
                    
                    except websockets.ConnectionClosed:
                        logger.warning("❌ Conexión cerrada. Intentando reconectar...")
                        break
                    except json.JSONDecodeError as e:
                        logger.error(f"❌ Error decodificando JSON: {e}")
                        continue
                    except Exception as e:
                        logger.error(f"❌ Error inesperado: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"❌ Error de conexión: {e}")
            logger.info("🔄 Intentando reconectar en 5 segundos...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        logger.info("🤖 Iniciando bot...")
        asyncio.run(monitor_transactions())
    except KeyboardInterrupt:
        logger.info("👋 Bot detenido por el usuario")