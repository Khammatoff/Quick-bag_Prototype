from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(100))
    role = Column(String(20))

    food_bags = relationship("FoodBag", back_populates="owner", cascade="all, delete")
    bookings = relationship("Booking", back_populates="user", cascade="all, delete")


class FoodBag(Base):
    __tablename__ = "food_bags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    description = Column(String(500))
    photo_url = Column(String(200), default="/placeholder.jpg")
    price = Column(Float)                  # добавлено поле цена без скидки
    discounted_price = Column(Float)
    quantity = Column(Integer)
    address = Column(String(200))
    pickup_time = Column(DateTime)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="food_bags")
    bookings = relationship("Booking", back_populates="food_bag", cascade="all, delete")


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    food_bag_id = Column(Integer, ForeignKey("food_bags.id"))
    quantity = Column(Integer)

    user = relationship("User", back_populates="bookings")
    food_bag = relationship("FoodBag", back_populates="bookings")
