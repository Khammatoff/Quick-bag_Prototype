from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import get_db
from app.utils import require_role

router = APIRouter(tags=["Users"])

@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = crud.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже зарегистрирован"
        )
    hashed_password = crud.hash_password(user.password)
    db_user = crud.create_user(db=db, email=user.email, hashed_password=hashed_password, role=user.role or "client")
    return db_user

@router.get("/", response_model=List[schemas.UserResponse])
def read_users(
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin"]))
):
    return crud.get_all_users(db)
