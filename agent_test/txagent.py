from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import logging
from supabase import create_client, Client
from datetime import datetime

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de Supabase
SUPABASE_URL = "https://efyeueofosjeljsrtqte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVmeWV1ZW9mb3NqZWxqc3J0cXRlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzkzMjAyMTUsImV4cCI6MjA1NDg5NjIxNX0.qcXx0RHrGDjdxs4HNhzoxSijK5m1H1yD309ccTyn3Jg"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="TX Agent Service")

class Transaction(BaseModel):
    to: str
    data: str
    value: str

class TransactionRequest(BaseModel):
    safeAddress: str
    safeTxHash: str
    LN_reason: str
    transactions: List[Transaction]
    warning: Optional[str] = None

@app.post("/process")
async def process_transaction(data: TransactionRequest):
    try:
        logger.info(f"Transacción recibida: {data}")
        
        if data.warning:
            # Insertar en Supabase
            try:
                result = supabase.table("live_chat").upsert({
                    "wallet": data.safeAddress,
                    "messages": f"{data.warning} {data.LN_reason}",
                    "timestamp": datetime.utcnow().isoformat()
                }).execute()
                
                logger.info(f"Warning guardado en Supabase: {result}")
            except Exception as e:
                logger.error(f"Error al guardar en Supabase: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Error guardando en base de datos: {str(e)}"
                )
        
        return {
            "status": "success",
            "message": "Transaction processed successfully",
            "data": {
                "safeAddress": data.safeAddress,
                "warning": data.warning
            }
        }
    except Exception as e:
        logger.error(f"Error procesando transacción: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing transaction: {str(e)}"
        )
if __name__ == "__main__":
    uvicorn.run("txagent:app", host="0.0.0.0", port=8001, reload=True)