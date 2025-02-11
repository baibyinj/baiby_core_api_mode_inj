from fastapi import APIRouter, HTTPException
from app.schemas import TransactionRequest, TransactionResponse
import hashlib

router = APIRouter()

@router.post("/agent/transaction/", response_model=TransactionResponse)
async def process_agent_transaction(transaction: TransactionRequest):
    try:
        # Generamos un hash simple de la transacción
        transaction_hash = hashlib.sha256(
            f"{transaction.transaction}{transaction.reason_why}".encode()
        ).hexdigest()
        
        return TransactionResponse(
            status="success",
            message=f"Transaction received with reason: {transaction.reason_why}",
            transaction_hash=transaction_hash
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing transaction: {str(e)}"
        ) 