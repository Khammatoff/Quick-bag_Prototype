from app.database import Base, engine
import app.models  # Чтобы зарегистрировались все модели

def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Таблицы успешно созданы!")

if __name__ == "__main__":
    create_tables()
