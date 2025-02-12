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

ZERO_ADDRESS = "0x00"

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
                            transactions = data.get("data", {}).get("transactions", [])
                            transaction_hash = data.get("data", {}).get("hash")
                            
                            logger.info(f"🔍 Analizando transacciones: {transactions}")
                            
                            # Verificar si alguna transacción tiene dirección 0x00
                            for tx in transactions:
                                if tx.get("to") == ZERO_ADDRESS:
                                    warning = {
                                        "type": "warning",
                                        "message": "Transacción a dirección cero detectada {ZERO_ADDRESS}",
                                        "transaction_hash": transaction_hash,
                                        "timestamp": datetime.utcnow().isoformat()
                                    }
                                    
                                    # Enviar warning
                                    await websocket.send(json.dumps(warning))
                                    logger.info(f"⚠️ Warning enviado: {warning}")
                                    break  # Solo enviamos un warning por lote de transacciones
                    
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