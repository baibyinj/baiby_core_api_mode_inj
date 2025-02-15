from fastapi import APIRouter, HTTPException
from app.schemas import TransactionRequest, TransactionResponse
from app.websocket_manager import ws_manager
from app.config import settings
import hashlib
import asyncio
import httpx
import logging
import json
from typing import Dict

router = APIRouter()
logger = logging.getLogger(__name__)

# Diccionario para mantener el seguimiento de las transacciones activas
active_transactions: Dict[str, asyncio.Event] = {}

def serialize_transaction(tx_request: TransactionRequest) -> dict:
    return {
        "transactions": [
            {
                "to": tx.to,
                "data": tx.data,
                "value": tx.value
            } for tx in tx_request.transactions
        ],
        "safeAddress": tx_request.safeAddress,
        "erc20TokenAddress": tx_request.erc20TokenAddress,
        "reason": tx_request.reason
    }

async def send_to_tx_agent(transaction_data: dict, warning: str = None):
    try:
        try:
            jsonresp = json.loads(warning)  # Intenta convertirlo a JSON
            bot_reason = jsonresp.get('message')
            status = jsonresp.get('status')
        except Exception as e:
            print(e)
            bot_reason = "None"  # Si falla, asigna None
            status = "approved"
            warning = "nada"
        print(bot_reason)
        print(status)
        async with httpx.AsyncClient() as client:
            data = {
                "safeAddress": transaction_data["safeAddress"],
                "erc20TokenAddress": transaction_data["erc20TokenAddress"],
                "reason": transaction_data["reason"],
                "transactions": transaction_data["transactions"],
                'bot_reason': bot_reason,
                'status': status,
                "warning": warning
            }
            logger.info(f"Enviando a txAgent: {data}")
            response = await client.post(
                f"{settings.TX_AGENT_URL}", 
                json=data,
                timeout=10.0
            )
            print(response.json())
            return response.json()
        
    except httpx.ConnectError:
        logger.error(f"No se pudo conectar a txAgent en {settings.TX_AGENT_URL}")
        return {"status": "error", "message": "txAgent no disponible"}
    except Exception as e:
        logger.error(f"Error al enviar a txAgent: {str(e)}")
        return {"status": "error", "message": str(e)}

async def process_transaction_with_timeout(tx_data: dict, transaction_hash: str):
    try:
        # Crear un evento para esta transacción
        event = asyncio.Event()
        active_transactions[transaction_hash] = event
        
        # Esperar por 5 segundos o hasta que llegue un warning
        try:
            logger.info(f"Esperando warnings para {transaction_hash}...")
            await asyncio.wait_for(event.wait(), timeout=5.0)
            warning = ws_manager.get_warning(transaction_hash)
            
            if warning:
                logger.info(f"Warning recibido para {transaction_hash}: {warning}")
                """ warning_data = {
                    "type": "warning",
                    "data": {
                        "warning": warning
                    }
                } """
                warning_data = json.dumps(warning)
                await send_to_tx_agent(tx_data, warning_data)
            else:
                logger.info(f"No se recibió warning para {transaction_hash}, esperando 5 segundos adicionales...")
                await asyncio.sleep(5.0)
                await send_to_tx_agent(tx_data)
        except asyncio.TimeoutError:
            logger.info(f"Timeout alcanzado para {transaction_hash}, esperando 5 segundos adicionales...")
            await asyncio.sleep(5.0)
            await send_to_tx_agent(tx_data)
            
    finally:
        # Limpiar recursos
        active_transactions.pop(transaction_hash, None)
        ws_manager.clear_warning(transaction_hash)

@router.post("/agent/transaction/", response_model=TransactionResponse)
async def process_agent_transaction(transaction: TransactionRequest):
    try:
        # Serializar la transacción completa para el hash y txAgent
        tx_data = serialize_transaction(transaction)
        
        # Generar hash usando todos los campos relevantes
        transaction_hash = hashlib.sha256(
            json.dumps(tx_data, sort_keys=True).encode()
        ).hexdigest()
        
        # Crear mensaje para los bots (solo las transactions)
        tx_message = {
            "type": "transaction",
            "data": {
                "transactions": tx_data["transactions"],
                "hash": transaction_hash,
                "safewallet": tx_data["safeAddress"]
            }
        }
        
        logger.info(f"Preparando broadcast de transacción: {tx_message}")
        
        # Enviar transacción a los bots conectados
        await ws_manager.broadcast(tx_message)
        logger.info("Broadcast completado")
        
        # Procesar la transacción en background
        asyncio.create_task(process_transaction_with_timeout(tx_data, transaction_hash))
        
        return TransactionResponse(
            status="success",
            message=f"Transaction received with reason: {transaction.reason}",
            transaction_hash=transaction_hash
        )
    except Exception as e:
        logger.error(f"Error en process_agent_transaction: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing transaction: {str(e)}"
        ) 