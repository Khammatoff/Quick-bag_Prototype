from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from . import models, schemas
from passlib.context import CryptContext
import logging

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# Пользователи
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_all_users(db: Session):
    return db.query(models.User).all()


def create_user(db: Session, email: str, hashed_password: str, role: str):
    db_user = models.User(email=email, hashed_password=hashed_password, role=role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


# Корзины
def create_food_bag(db: Session, food_bag: schemas.FoodBagCreate, user_id: int):
    db_food_bag = models.FoodBag(
        **food_bag.dict(),
        owner_id=user_id,
        photo_url="/placeholder.jpg"
    )
    db.add(db_food_bag)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logging.error(f"Failed to commit new food bag: {e}")
        raise
    db.refresh(db_food_bag)
    logging.info(f"Food bag created with id {db_food_bag.id}")
    return db_food_bag


def get_food_bag(db: Session, food_bag_id: int):
    return db.query(models.FoodBag).filter(models.FoodBag.id == food_bag_id).first()


def get_food_bags(db: Session, current_user=None, address: str = None, filter_expired: bool = False):
    query = db.query(models.FoodBag).join(models.User, models.FoodBag.owner)

    if filter_expired:
        query = query.filter(models.FoodBag.pickup_time > datetime.utcnow())

    if current_user and current_user.role == "establishment":
        query = query.filter(models.FoodBag.owner_id == current_user.id)

    if address:
        query = query.filter(models.FoodBag.address.ilike(f"%{address}%"))
    return query.all()
    logging.info(
        f"Fetched {len(result)} food bags for user {current_user.email if current_user else 'anonymous'} with filter '{address}'")
    return result


def update_food_bag(db: Session, food_bag_id: int, food_bag_update: schemas.FoodBagCreate, current_user):
    if current_user.role == 'admin':
        db_food_bag = db.query(models.FoodBag).filter(models.FoodBag.id == food_bag_id).first()
    else:
        db_food_bag = db.query(models.FoodBag).filter(models.FoodBag.id == food_bag_id,
                                                     models.FoodBag.owner_id == current_user.id).first()

    if not db_food_bag:
        return None

    for key, value in food_bag_update.dict().items():
        setattr(db_food_bag, key, value)
    db.commit()
    db.refresh(db_food_bag)
    return db_food_bag


def delete_food_bag(db: Session, food_bag_id: int, current_user):
    if current_user.role == 'admin':
        db_food_bag = db.query(models.FoodBag).filter(models.FoodBag.id == food_bag_id).first()
    else:
        db_food_bag = db.query(models.FoodBag).filter(models.FoodBag.id == food_bag_id,
                                                     models.FoodBag.owner_id == current_user.id).first()

    if not db_food_bag:
        return False

    db.delete(db_food_bag)
    db.commit()
    return True


# Бронирования
def book_food_bag(db: Session, booking: schemas.BookingCreate, user_id: int):
    food_bag = get_food_bag(db, booking.food_bag_id)
    if not food_bag:
        raise HTTPException(status_code=404, detail="Food bag not found")
    if food_bag.quantity < booking.quantity:
        raise HTTPException(status_code=400, detail="Not enough food bags available")

    db_booking = models.Booking(**booking.dict(), user_id=user_id)
    food_bag.quantity -= booking.quantity

    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking


# Автоматическое удаление просроченных корзин
def delete_expired_food_bags(db: Session):
    now = datetime.utcnow()
    expired_bags = db.query(models.FoodBag).filter(models.FoodBag.pickup_time <= now).all()
    count = len(expired_bags)
    for bag in expired_bags:
        db.delete(bag)
    db.commit()
    return count
