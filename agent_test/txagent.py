from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI(title="TX Agent Service")

class TransactionData(BaseModel):
    transaction: dict
    warning: Optional[str] = None

@app.post("/process")
async def process_transaction(data: TransactionData):
    try:
        # Log de la transacción recibida
        print(f"Transacción recibida: {data.transaction}")
        if data.warning:
            print(f"Warning recibido: {data.warning}")
        
        return {
            "status": "success",
            "message": "Transaction processed successfully",
            "received_data": data.dict()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing transaction: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run("txagent:app", host="0.0.0.0", port=8001, reload=True)