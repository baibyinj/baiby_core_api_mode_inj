from fastapi import APIRouter, HTTPException
from app.schemas import TransactionRequest, TransactionResponse
from app.websocket_manager import ws_manager
from app.config import settings
import hashlib
import asyncio
import httpx
import logging
import json

router = APIRouter()
logger = logging.getLogger(__name__)

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
        "safeTxHash": tx_request.safeTxHash,
        "LN_reason": tx_request.LN_reason
    }

async def send_to_tx_agent(transaction_data: dict, warning: str = None):
    try:
        async with httpx.AsyncClient() as client:
            data = {
                "transaction": transaction_data,
                "warning": warning
            }
            logger.info(f"Enviando a txAgent: {data}")
            response = await client.post(
                f"{settings.TX_AGENT_URL}/process", 
                json=data,
                timeout=10.0
            )
            return response.json()
    except httpx.ConnectError:
        logger.error(f"No se pudo conectar a txAgent en {settings.TX_AGENT_URL}")
        return {"status": "error", "message": "txAgent no disponible"}
    except Exception as e:
        logger.error(f"Error al enviar a txAgent: {str(e)}")
        return {"status": "error", "message": str(e)}

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
                "hash": transaction_hash
            }
        }
        
        logger.info(f"Preparando broadcast de transacción: {tx_message}")
        
        # Enviar transacción a los bots conectados
        await ws_manager.broadcast(tx_message)
        logger.info("Broadcast completado")
        
        # Esperar respuestas durante 5 segundos
        logger.info("Esperando warnings...")
        warnings = await ws_manager.receive_warnings(timeout=5.0)
        
        if warnings:
            # Si hay advertencias, enviar inmediatamente a txAgent
            logger.info(f"Warning recibido: {warnings[0]}")
            result = await send_to_tx_agent(tx_data, warnings[0])
            if result["status"] == "error":
                logger.warning(f"Error al enviar a txAgent: {result['message']}")
        else:
            # Esperar 5 segundos antes de enviar a txAgent
            logger.info("No se recibieron warnings, esperando 5 segundos...")
            await asyncio.sleep(5.0)
            await send_to_tx_agent(tx_data)
        
        return TransactionResponse(
            status="success",
            message=f"Transaction received with reason: {transaction.LN_reason}",
            transaction_hash=transaction_hash
        )
    except Exception as e:
        logger.error(f"Error en process_agent_transaction: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing transaction: {str(e)}"
        ) 