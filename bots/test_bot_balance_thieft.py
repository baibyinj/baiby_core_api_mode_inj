import asyncio
import websockets
import json
import logging
from datetime import datetime
import traceback
from web3 import Web3

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuración
SAFE_ADDRESS_TO_CHECK = "0x88"
RPC_URL = "https://multi-quaint-leaf.quiknode.pro/da0d39e9df88697276020a15c017af0764d66327"  # Ajusta esto según tu red
w3 = Web3(Web3.HTTPProvider(RPC_URL))

async def get_native_balance(address: str) -> int:
    try:
        logger.info(f"🔍 Intentando obtener balance para {address}")
        if not w3.is_address(address):
            logger.error(f"❌ Dirección inválida: {address}")
            return 0
            
        balance = w3.eth.get_balance(address)
        logger.info(f"💰 Balance nativo obtenido para {address}: {balance}")
        return balance
    except Exception as e:
        logger.error(f"❌ Error obteniendo balance: {e}")
        logger.error(f"Stack trace: {traceback.format_exc()}")
        return 0

async def monitor_transactions():
    uri = "ws://localhost:8000/ws/bot"
    
    while True:  # Bucle principal para reconexión
        try:
            async with websockets.connect(uri) as websocket:
                logger.info("✅ Bot conectado al servidor")
                
                while True:
                    try:
                        message = await websocket.recv()
                        logger.info(f"📩 Mensaje recibido: {message}")
                        
                        data = json.loads(message)
                        logger.info(f"🔄 Datos parseados: {data}")
                        
                        if data.get("type") == "transaction":
                            transactions = data.get("data", {}).get("transactions", [])
                            transaction_hash = data.get("data", {}).get("hash")
                            safewallet = data.get("data", {}).get("safewallet")
                            
                            logger.info(f"🔍 Analizando transacción para safewallet: {safewallet}")
                            
                            if not safewallet:
                                logger.warning("⚠️ No se encontró safewallet en el mensaje")
                                continue
                                
                            # Obtener balance nativo
                            current_balance = await get_native_balance(safewallet)
                            logger.info(f"💰 Balance actual: {current_balance}")
                            
                            # Verificar cada transacción
                            for tx in transactions:
                                value = int(tx.get("value", "0"), 16) if tx.get("value", "0").startswith("0x") else int(tx.get("value", "0"))
                                logger.info(f"💱 Valor de la transacción: {value}")
                                
                                if value == current_balance and value > 0:
                                    warning = {
                                        "type": "warning",
                                        "message": f"⚠️ Posible vaciado de wallet detectado! La transacción usa todo el balance nativo ({value} wei)",
                                        "transaction_hash": transaction_hash,
                                        "status": "warning",
                                        "safewallet": safewallet,
                                        "current_balance": str(current_balance),
                                        "tx_value": str(value),
                                        "timestamp": datetime.utcnow().isoformat()
                                    }
                                    
                                    await websocket.send(json.dumps(warning))
                                    logger.info(f"⚠️ Warning enviado: {warning}")
                                    break
                    
                    except websockets.ConnectionClosed:
                        logger.warning("❌ Conexión cerrada. Intentando reconectar...")
                        break
                    except json.JSONDecodeError as e:
                        logger.error(f"❌ Error decodificando JSON: {e}")
                        continue
                    except Exception as e:
                        logger.error(f"❌ Error inesperado: {e}")
                        logger.error(f"Stack trace: {traceback.format_exc()}")
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