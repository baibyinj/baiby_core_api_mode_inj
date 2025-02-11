from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas import Item, ItemBase

router = APIRouter()

# Simulamos una base de datos con una lista
items_db = []

@router.get("/items/", response_model=List[Item])
def get_items():
    return items_db

@router.post("/items/", response_model=Item)
def create_item(item: ItemBase):
    new_item = Item(
        id=len(items_db) + 1,
        name=item.name,
        description=item.description,
        price=item.price
    )
    items_db.append(new_item)
    return new_item

@router.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int):
    if item_id > len(items_db):
        raise HTTPException(status_code=404, detail="Item no encontrado")
    return items_db[item_id - 1] 