from pydantic import BaseModel, Field
from typing import List

class ItemBase(BaseModel):
    name: str
    description: str | None = None
    price: float

class Item(ItemBase):
    id: int 

class Transaction(BaseModel):
    to: str
    data: str
    value: str

class TransactionRequest(BaseModel):
    transactions: List[Transaction]
    safeAddress: str
    safeTxHash: str
    LN_reason: str

class TransactionResponse(BaseModel):
    status: str
    message: str
    transaction_hash: str 