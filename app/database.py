import os

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv

# Load the variables from the .env file into the system environment
load_dotenv()

# Важно: используем префикс sqlite+aiosqlite для асинхронной работы
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")


# 1. Создаем асинхронный движок (Async Engine)
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False} # Нужно только для SQLite
)

# 2. Создаем фабрику асинхронных сессий.
# expire_on_commit=False — важная настройка для async, чтобы объекты не "протухали" после комита.
AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# 3. Базовый класс для моделей (современный синтаксис SQLAlchemy 2.0)
class Base(DeclarativeBase):
    pass

# 4. Dependency (Зависимость).
# Это асинхронный генератор.
async def get_db():
    # Используем async with — это гарантирует, что сессия закроется корректно
    async with AsyncSessionLocal() as db:
        yield db
