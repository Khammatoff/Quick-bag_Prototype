import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "foodbasket")

SQLALCHEMY_DATABASE_URL = settings.database_url

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Перенесём импорт моделей и utils внутрь функций, чтобы избежать циклических импортов
def init_db():
    from . import models, utils  # Локальный импорт

    # Создаём таблицы
    models.Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Создаем администратора если его нет
        admin_email = "admin@admin"
        admin = db.query(models.User).filter(models.User.email == admin_email).first()
        if not admin:
            hashed_password = utils.hash_password("admin")
            admin = models.User(
                email=admin_email,
                hashed_password=hashed_password,
                role="admin"
            )
            db.add(admin)
            db.commit()
    finally:
        db.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()