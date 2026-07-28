import logging


from app.config import redis_client
from app.logging_config import setup_logging
from fastapi import FastAPI
# Импортируем наш новый модуль с роутером
from app.routers import users, upload
from app.routers import profiles

setup_logging()
logger = logging.getLogger("fastapi")


# Проверка подключения
try:
    # Попытка выполнить команду PING
    response = redis_client.ping()
    if response:
        logger.info("Подключение к Redis успешно!")
    else:
        logger.info("Не удалось подключиться к Redis.")
except Exception as e:
    logger.info(f"Произошла ошибка : {e}")

app = FastAPI(title="My Architecture App")

# Подключаем роутер к главному приложению.
# Это похоже на подключение плагина.
app.include_router(users.router)

app.include_router(profiles.router)

app.include_router(upload.router)

@app.get("/")
def root():
    return {"message": "Приложение работает!"}
