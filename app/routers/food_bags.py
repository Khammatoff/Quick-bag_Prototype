from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app import schemas, crud
from app.database import get_db
from app.utils import get_current_user, require_role

router = APIRouter(tags=["Food Bags"])


@router.post("/", response_model=schemas.FoodBagResponse)
async def create_food_bag(
    food_bag: schemas.FoodBagCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["establishment", "admin"]))
):
    return crud.create_food_bag(db=db, food_bag=food_bag, user_id=current_user.id)


@router.get("/", response_model=list[schemas.FoodBagResponse])
async def read_food_bags(
    address: str = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Только не просроченные корзины
    return crud.get_food_bags(db=db, current_user=current_user, address=address, filter_expired=True)


@router.put("/{food_bag_id}", response_model=schemas.FoodBagResponse)
async def update_food_bag(
    food_bag_id: int,
    food_bag_update: schemas.FoodBagCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    updated_food_bag = crud.update_food_bag(
        db=db,
        food_bag_id=food_bag_id,
        food_bag_update=food_bag_update,
        current_user=current_user
    )
    if not updated_food_bag:
        raise HTTPException(status_code=404, detail="Food bag not found or permission denied")
    return updated_food_bag


@router.delete("/{food_bag_id}")
async def delete_food_bag(
    food_bag_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["establishment", "admin"]))
):
    success = crud.delete_food_bag(db=db, food_bag_id=food_bag_id, current_user=current_user)
    if not success:
        raise HTTPException(status_code=404, detail="Food bag not found or permission denied")
    return {"message": "Food bag deleted successfully"}
