import os
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db  # Импортируем наш асинхронный генератор
from app.models import User
from app.schemas import UserResponse, UserCreate

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponse)
async def create_user(
        user: UserCreate,
        # FastAPI сам вызовет get_db, дождется сессии и передаст её сюда
        db: AsyncSession = Depends(get_db)
):
    # Хешируем пароль (в реальном проекте используйте Bcrypt!)
    fake_hashed_password = f"{os.getenv('SECRET')}_{user.password}"

    db_user = User(email=user.email, hashed_password=fake_hashed_password)

    # Добавляем в сессию (здесь await не нужен, это операция в памяти)
    db.add(db_user)

    # А вот здесь мы "отпускаем" управление, пока база сохраняет данные.
    # В это время сервер может обрабатывать запросы других пользователей!
    await db.commit()

    # Обновляем объект данными из базы (например, получаем присвоенный ID)
    await db.refresh(db_user)

    return db_user

@router.get("/", response_model=List[UserResponse])
async def get_users(
        limit=100,
        # FastAPI сам вызовет get_db, дождется сессии и передаст её сюда
        db: AsyncSession = Depends(get_db)
):
    # Construct the query using modern SQLAlchemy 2.0 select()
    query = select(User).limit(limit)

    # Await the execution of the query asynchronously
    result = await db.execute(query)

    # Extract the scalar objects (the User instances)
    users = result.scalars().all()
    return users
