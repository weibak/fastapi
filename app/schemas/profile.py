from pydantic import BaseModel, EmailStr


# Базовая схема с общими полями, которые есть всегда
class ProfileBase(BaseModel):
    first_name: str
    last_name: str
    bio: str
    

# Схема для ОТВЕТА (Output DTO)
# Эти данные мы отдаем клиенту
class ProfileResponse(ProfileBase):
    id: int
    first_name: str
    last_name: str
    bio: str

    # Обратите внимание: поля password здесь НЕТ. 
    # Мы отфильтровали его на уровне схемы. Pydantic просто проигнорирует его
    # при формировании JSON, даже если в модели базы данных оно есть.

    # Эта настройка нужна, чтобы Pydantic мог читать данные 
    # прямо из объектов SQLAlchemy (ORM-модели).
    # P.S. В старых версиях Pydantic v1 это называлось 'orm_mode = True'.
    # Мы же используем Pydantic v2
    class Config:
        from_attributes = True
