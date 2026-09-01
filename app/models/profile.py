from app.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict, field_validator


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)

    # Внешний ключ с unique=True для один-к-одному
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    # Отношение с backref
    user = relationship("User", backref="profile", uselist=False)

    first_name = Column(String)
    last_name = Column(String)
    bio = Column(String)

class ProfilePydantic(BaseModel):
    id: int
    user_id: int
    first_name: str
    last_name: str
    bio: str | None = None

    model_config = ConfigDict(from_attributes=True)
    
    @field_validator('first_name', mode='before')
    def validate_first_name(cls, v):
        if isinstance(v, int):
            return str(v)
        elif isinstance(v, str):
            return v
        else:
            raise ValueError("Имя должно быть строкой или числом")

    @field_validator('last_name', mode='before')
    def validate_last_name(cls, v):
        if isinstance(v, int):
            return str(v)
        elif isinstance(v, str):
            return v
        else:
            raise ValueError("Имя должно быть строкой или числом")
