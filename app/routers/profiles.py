import os
from typing import List

from app.models.profile import Profile
from fastapi import status, HTTPException
from app.schemas import UserResponse, UserCreate
from app.schemas.profile import ProfileResponse
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db  # Импортируем наш асинхронный генератор
from app.models import User

router = APIRouter(prefix="/profiles", tags=["Profiles"])


@router.post("/register", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def register_user(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    # 1. Проверяем, существует ли пользователь (используем асинхронный select)
    query = select(User).where(User.email == payload.email)
    result = await db.execute(query)
    db_user = result.scalar_one_or_none()

    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered"
        )

    # 2. Хешируем пароль
    # Хешируем пароль (в реальном проекте используйте Bcrypt!)
    fake_hashed_password = f"{os.getenv('SECRET')}_{payload.password}"

    # 3. Создаем объект пользователя и профиля
    new_user = User(
        email=payload.email,
        hashed_password=fake_hashed_password
    )

    new_profile = Profile(
        user_id=new_user.id,
        first_name=payload.profile.first_name,
        last_name=payload.profile.last_name,
        bio=payload.profile.bio
    )

    # Связываем их через ORM-отношение
    new_user.profile = [new_profile]

    # 4. Сохраняем в базу данных в рамках единой асинхронной транзакции
    try:
        db.add(new_user)
        db.add(new_profile)
        await db.commit()
        await db.refresh(new_user)  # Обновляем объект, чтобы подгрузить сгенерированные id
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{e}"
        )

    return new_profile

@router.get("/", response_model=List[ProfileResponse])
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
