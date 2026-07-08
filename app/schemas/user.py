from pydantic import BaseModel, EmailStr


# Базовая схема с общими полями, которые есть всегда
class UserBase(BaseModel):
    email: EmailStr


# Схема для СОЗДАНИЯ пользователя (Input DTO)
# Клиент отправляет нам эти данные
class UserCreate(UserBase):
    password: str  # Клиент шлет сырой пароль, мы его валидируем здесь


# Схема для ОТВЕТА (Output DTO)
# Эти данные мы отдаем клиенту
class UserResponse(UserBase):
    id: int
    is_active: bool

    # Обратите внимание: поля password здесь НЕТ. 
    # Мы отфильтровали его на уровне схемы. Pydantic просто проигнорирует его
    # при формировании JSON, даже если в модели базы данных оно есть.

    # Эта настройка нужна, чтобы Pydantic мог читать данные 
    # прямо из объектов SQLAlchemy (ORM-модели).
    # P.S. В старых версиях Pydantic v1 это называлось 'orm_mode = True'.
    # Мы же используем Pydantic v2
    class Config:
        from_attributes = True
