import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas, crud, models
from app.database import get_db
from app.utils import get_current_user

router = APIRouter(
    tags=["Bookings"]
)

@router.get("/ping")
def ping():
    return {"ping": "pong"}

@router.post("/", response_model=schemas.BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    booking: schemas.BookingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    logging.info(
        f"Booking attempt by user_id={current_user.id} "
        f"email={current_user.email} role={current_user.role} "
        f"food_bag_id={booking.food_bag_id} quantity={booking.quantity}"
    )

    # Проверка роли пользователя - только "client" может бронировать
    if current_user.role != "client":
        logging.warning(f"Booking forbidden for user_id={current_user.id} with role={current_user.role}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only clients can book food bags")

    # Проверка существования корзины в БД
    food_bag = crud.get_food_bag(db, booking.food_bag_id)
    if not food_bag:
        logging.warning(f"Food bag with id={booking.food_bag_id} not found for booking")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food bag not found")

    # Проверка доступного количества корзин
    if food_bag.quantity < booking.quantity:
        logging.warning(
            f"Not enough quantity for food_bag_id={booking.food_bag_id}: requested={booking.quantity}, available={food_bag.quantity}"
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough food bags available")

    # Попытка создать бронирование в базе
    try:
        db_booking = crud.book_food_bag(db, booking, current_user.id)
        logging.info(f"Booking created successfully with id={db_booking.id} for user_id={current_user.id}")
        return db_booking
    except Exception as e:
        logging.error(f"Error occurred while creating booking: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create booking")
