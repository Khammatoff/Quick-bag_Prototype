from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
import os
import logging

from app.database import init_db, SessionLocal
from app.routers import auth, users, food_bags, bookings
from sqlalchemy.orm import Session
from app.crud import delete_expired_food_bags
from fastapi_utils.tasks import repeat_every

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI()

# Инициализация базы данных
init_db()

# Подключение роутеров API
app.include_router(auth, prefix="/auth", tags=["Auth"])
app.include_router(users, prefix="/users", tags=["Users"])
app.include_router(food_bags, prefix="/food-bags", tags=["Food Bags"])
app.include_router(bookings, prefix="/bookings", tags=["Bookings"])

for route in app.routes:
    logging.info(f"Registered route: path={route.path}, name={route.name}, methods={route.methods}")

# Определяем абсолютный путь к папке со статикой относительно этого файла
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Монтируем папку со статикой по пути /static
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Эндпоинт для отдачи index.html при обращении к /
@app.get("/")
async def read_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"detail": "index.html not found"}

# Фоновая задача для удаления просроченных корзин, повторяется раз в час
@app.on_event("startup")
@repeat_every(seconds=60 * 60)  # каждые 60 минут
def periodic_cleanup_expired_food_bags_task() -> None:
    db: Session = SessionLocal()
    try:
        count = delete_expired_food_bags(db)
        if count > 0:
            print(f"Deleted {count} expired food bags")
    finally:
        db.close()
