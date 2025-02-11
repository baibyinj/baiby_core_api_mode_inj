import asyncio
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def monitor_transactions():
    uri = "ws://localhost:8000/ws/bot"
    
    while True:  # Bucle principal para reconexión
        try:
            async with websockets.connect(uri) as websocket:
                logger.info("Bot conectado al servidor...")
                
                while True:
                    try:
                        # Recibir mensaje
                        message = await websocket.recv()
                        data = json.loads(message)
                        print(data)
                        
                        if data["type"] == "transaction":
                            transaction = data["data"]
                            logger.info(f"Transacción recibida: {transaction}")
                            
                            # Verificar si la palabra "oso" está en la transacción
                            transaction_str = json.dumps(transaction).lower()
                            if "oso" in transaction_str:
                                warning = {
                                    "type": "warning",
                                    "message": "peludo",
                                    "transaction_hash": transaction["hash"]
                                }
                                
                                # Enviar warning
                                await websocket.send(json.dumps(warning))
                                logger.info(f"Warning enviado: {warning}")
                    
                    except websockets.ConnectionClosed:
                        logger.warning("Conexión cerrada. Intentando reconectar...")
                        break
                    except json.JSONDecodeError:
                        logger.error("Error decodificando JSON")
                        continue
                    except Exception as e:
                        logger.error(f"Error inesperado: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error de conexión: {e}")
            await asyncio.sleep(5)  # Esperar antes de intentar reconectar

if __name__ == "__main__":
    try:
        asyncio.run(monitor_transactions())
    except KeyboardInterrupt:
        logger.info("Bot detenido por el usuario")