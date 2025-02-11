from pydantic import BaseModel

class ItemBase(BaseModel):
    name: str
    description: str | None = None
    price: float

class Item(ItemBase):
    id: int 

class TransactionRequest(BaseModel):
    transaction: str  # La transacción en formato hex
    reason_why: str  # La razón proporcionada por el agente

class TransactionResponse(BaseModel):
    status: str
    message: str
    transaction_hash: str 