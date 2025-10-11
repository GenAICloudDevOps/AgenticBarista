from fastapi import APIRouter, HTTPException
from app.models.menu import MenuItem, MenuItemSchema
from typing import List

router = APIRouter()

@router.get("/menu", response_model=List[MenuItemSchema])
async def get_menu():
    items = await MenuItem.filter(available=True)
    return [MenuItemSchema.from_orm(item) for item in items]

@router.get("/menu/{item_id}", response_model=MenuItemSchema)
async def get_menu_item(item_id: int):
    try:
        item = await MenuItem.get(id=item_id)
        return MenuItemSchema.from_orm(item)
    except:
        raise HTTPException(status_code=404, detail="Menu item not found")

@router.post("/menu", response_model=MenuItemSchema)
async def create_menu_item(item: MenuItemSchema):
    menu_item = await MenuItem.create(**item.dict(exclude={"id"}))
    return MenuItemSchema.from_orm(menu_item)
