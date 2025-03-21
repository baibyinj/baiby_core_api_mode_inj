import asyncio
import websockets
import json
import logging
from datetime import datetime
from goplus.address import Address

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def check_address_security(address: str) -> tuple[bool, str]:
    try:
        data = Address(access_token=None).address_security(address=address)
        
        if data.get("code") != 1:
            return False, "Error checking address security"
        
        result = data.get("result", {})
        
        # Filtrar las categorías que tienen valor "1"
        flagged_categories = [
            category.replace("_", " ").title()
            for category, value in result.items()
            if value == "1" and category != "data_source"
        ]
        
        if flagged_categories:
            warning_message = "Warning: destination address is flagged with these categories: " + ", ".join(flagged_categories)
            return True, warning_message
        
        return False, ""
        
    except Exception as e:
        logger.error(f"Error checking address security: {e}")
        return False, f"Error checking address: {str(e)}"

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
                            
                            # Verificar cada transacción con GoPlus
                            for tx in transactions:
                                destination_address = tx.get("to")
                                if not destination_address:
                                    continue
                                    
                                is_malicious, warning_message = await check_address_security(destination_address)
                                
                                if is_malicious:
                                    warning = {
                                        "type": "warning",
                                        "message": warning_message,
                                        "transaction_hash": transaction_hash,
                                        "status": "warning",
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