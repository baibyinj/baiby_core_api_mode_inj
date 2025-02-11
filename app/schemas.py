from pydantic import BaseModel

class ItemBase(BaseModel):
    name: str
    description: str | None = None
    price: float

class Item(ItemBase):
    id: int 