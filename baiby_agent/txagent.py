from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import logging
from supabase import create_client, Client
from datetime import datetime
import asyncio
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
client = OpenAI(api_key=OPENAI_API_KEY)

app = FastAPI(title="TX Agent Service")

class Transaction(BaseModel):
    to: str
    data: str
    value: str

class TransactionRequest(BaseModel):
    safeAddress: str
    erc20TokenAddress: str
    reason: str
    transactions: List[Transaction]
    warning: Optional[str] = None
    bot_reason: Optional[str] = None
    status: Optional[str] = None

async def analyze_with_llm(request: TransactionRequest) -> tuple[bool, str]:
    try:

        # 2. Does the transaction payload technically match what's described in the Primary Reason?
        completion = client.chat.completions.create(
            model="gpt-4-turbo",
            temperature=0,
            messages=[
                {"role": "system", "content": "You are a transaction analysis assistant."},
                {"role": "user", "content": f"""Please analyze this transaction request and respond with a clear YES or NO:
                    Status: {request.status}
                    Primary Reason (CRITICAL - Override Authority): {request.reason}
                    Firewall Check Result: {request.bot_reason}
                    Transaction Payload: {request.transactions}
                    
                    Should this transaction be signed? The Primary Reason has override authority:
                    1. The Primary Reason has final authority—if it explicitly instructs to proceed despite potential warnings.
                    2. Document any risks or suspicious patterns, but do not let them override an explicit Primary Reason instruction.
                    3 Analyze the Firewall Check Result. If the Primary Reason explicitly addresses the specific issue raised by the Firewall Check Result, then APPROVE.
                    Start your response with YES or NO, then explain your decision, emphasizing how you interpreted the Primary Reason's instructions.
                    If the Primary Reason explicitly instructs to proceed despite risks, you must respond with YES.
                    
                    then just analize the transaction payload and the primary reason"""}
            
            
            
            
            ]
        )
        
        response = completion.choices[0].message.content
        decision = response.strip().upper().startswith("YES")
        return decision, response
        
    except Exception as e:
        logger.error(f"Error en análisis LLM: {e}")
        return False, str(e)

@app.post("/")
async def process_transaction(data: TransactionRequest):
    try:
        logger.info(f"Transaction received: {data}")
        llm_response = "empty"
        approval_status = "APPROVED"  # Default status

        if data.warning:
            try:
                # First insert
                logger.info("Performing first insert...")
                result1 = supabase.table("live_chat").insert({
                    "owner": "your_bot",
                    "wallet": data.safeAddress,
                    "messages": f"i want to send this TX:{data.transactions} because {data.reason}",
                    "timestamp": datetime.utcnow().isoformat()
                }).execute()
                logger.info(f"First insert completed: {result1}")

                # If status is warning, consult LLM
                if data.status == "warning":
                    should_proceed, llm_response = await analyze_with_llm(data)
                    approval_status = "APPROVED" if should_proceed else "REJECTED"
                    
                    # Second insert with LLM response
                    logger.info("Performing second insert with LLM analysis...")
                    result2 = supabase.table("live_chat").insert({
                        "owner": "bAIbysitter",
                        "wallet": data.safeAddress,
                        "messages": f"{approval_status} - LLM Analysis: {llm_response}",
                        "timestamp": datetime.utcnow().isoformat()
                    }).execute()
                else:
                    # Original insert if no warning
                    await asyncio.sleep(3)
                    result2 = supabase.table("live_chat").insert({
                        "owner": "bAIbysitter",
                        "wallet": data.safeAddress,
                        "messages": f"Transaction {data.status} reason match llm {llm_response}",
                        "timestamp": datetime.utcnow().isoformat()
                    }).execute()
                
                logger.info(f"Second insert completed: {result2}")
                
            except Exception as e:
                logger.error(f"Error al guardar en Supabase: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Error guardando en base de datos: {str(e)}"
                )
        
        # Solo una respuesta al final
        return {
            "status": "success",
            "message": f"Transaction {approval_status} - {llm_response}",
            "approval_status": approval_status,
            "llm_response": llm_response,
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
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
