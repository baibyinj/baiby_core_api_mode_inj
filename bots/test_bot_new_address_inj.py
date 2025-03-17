import asyncio
import websockets
import json
import logging
import sys
from datetime import datetime
import traceback
from dotenv import load_dotenv
import os
from pyinjective.async_client import AsyncClient
from pyinjective.core.network import Network
import base64
# Cargar variables de entorno
load_dotenv()

# Configurar logging específico para websockets para ignorar ping/pong
logging.getLogger('websockets').setLevel(logging.WARNING)

# Configuración detallada de logging
logging.basicConfig(
    level=logging.INFO,  # Cambiado a INFO para evitar mensajes de debug
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),  # Output a stdout con flush
        logging.FileHandler('bot_inj.log', mode='a')  # Output a archivo en modo append
    ],
    force=True  # Forzar la configuración
)

# Configurar stdout para que haga flush inmediatamente
sys.stdout.reconfigure(line_buffering=True)

logger = logging.getLogger(__name__)

# Asegurarse de que los handlers hagan flush inmediatamente
for handler in logger.handlers:
    if isinstance(handler, logging.StreamHandler):
        handler.flush = sys.stdout.flush

# Configuración desde variables de entorno
WS_BOT_URL = os.getenv('WS_BOT_URL')
if not WS_BOT_URL:
    print("❌ WS_BOT_URL no encontrado en .env")  # Print directo para debug
    logger.critical("❌ WS_BOT_URL no encontrado en .env")
    WS_BOT_URL = 'ws://localhost:8000/ws/bot'

print(f"🔧 Iniciando bot con URL: {WS_BOT_URL}")  # Print directo para debug
logger.info(f"🔧 Configuración cargada - WS_BOT_URL: {WS_BOT_URL}")

async def check_first_transfer(from_address: str, to_address: str) -> bool:
    """Checks if this is the first transfer from from_address to to_address"""
    try:
        logger.debug(f"🔍 Checking transfers from {from_address} to {to_address}")
        network = Network.testnet()
        client = AsyncClient(network=network)
        
        # Get all transactions from sender
        txs = await client.fetch_account_txs(from_address)
        
        if not txs or 'data' not in txs:
            return True
            
        # Check each transaction
        for tx in txs['data']:
            try:
                messages_base64 = tx.get('messages', '')
                if messages_base64:
                    messages = base64.b64decode(messages_base64)
                    decoded_messages = json.loads(messages)
                    
                    for msg in decoded_messages:
                        if msg.get('type') == '/cosmos.bank.v1beta1.MsgSend':
                            if msg.get('value', {}).get('to_address') == to_address:
                                logger.info(f"🔍 Not Found previous transfer to {to_address}")
                                return False
            except Exception as e:
                logger.error(f"Error processing transaction: {e}")
                continue
                
        logger.info(f"✅ First transfer detected to {to_address}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error checking transfers: {e}")
        logger.error(f"Stack trace: {traceback.format_exc()}")
        return True

async def monitor_transactions():
    while True:
        try:
            async with websockets.connect(WS_BOT_URL) as websocket:
                logger.info("🔌 Connected to WebSocket")
                
                while True:
                    message = await websocket.recv()
                    data = json.loads(message)
                    
                    if data.get("type") == "transaction":
                        transactions = data.get("data", {}).get("transactions", [])
                        transaction_hash = data.get("data", {}).get("hash")
                        safewallet = data.get("data", {}).get("safewallet")
                        
                        if not safewallet:
                            continue
                            
                        for tx in transactions:
                            to_address = tx.get("to")
                            if not to_address:
                                continue
                                
                            is_first_transfer = await check_first_transfer(safewallet, to_address)
                            
                            if is_first_transfer:
                                warning = {
                                    "type": "warning",
                                    "message": f"⚠️ First transfer detected to: {to_address}",
                                    "transaction_hash": transaction_hash,
                                    "status": "warning",
                                    "safewallet": safewallet,
                                    "destination": to_address,
                                    "timestamp": datetime.utcnow().isoformat()
                                }
                                
                                await websocket.send(json.dumps(warning))
                                break
                                
        except Exception as e:
            logger.error(f"❌ Error in monitor_transactions: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        print("🤖 Starting bot...")
        logger.info("🤖 Starting new address monitoring bot for Injective...")
        logger.info(f"📡 Using WebSocket URL: {WS_BOT_URL}")
        asyncio.run(monitor_transactions())
    except KeyboardInterrupt:
        print("👋 Bot stopped by user")
        logger.info("👋 Bot stopped by user")
    except Exception as e:
        print(f"🚨 Critical error: {e}")
        logger.critical(f"🚨 Critical error: {e}")
        logger.critical(f"Stack trace: {traceback.format_exc()}")