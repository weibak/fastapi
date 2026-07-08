from app.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

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
