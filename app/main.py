import logging
import os

from app.api import router_socket, router_page
from app.config import redis_client
from app.database import create_application_logs, create_document_store
from app.logging_config import setup_logging
from fastapi import FastAPI
# Импортируем наш новый модуль с роутером
from app.routers import users, upload, ai_chat
from app.routers import profiles
from fastapi.staticfiles import StaticFiles

setup_logging()
logger = logging.getLogger("fastapi")

create_application_logs()
create_document_store()

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

app = FastAPI(title="My Architecture App",
              version="1.0.1",
              swagger_ui_parameters={"deepLinking": True, "syntaxHighlight": {"theme": "obsidian"}},
              docs_url=None if os.getenv("ENV") == "production" else "/docs",
              redoc_url=None if os.getenv("ENV") == "production" else "/redoc"
              )
app.mount('/static', StaticFiles(directory='app/static'), 'static')

# Подключаем роутер к главному приложению.
# Это похоже на подключение плагина.
app.include_router(users.router)

app.include_router(profiles.router)

app.include_router(upload.router)

app.include_router(router_socket.router)
app.include_router(router_page.router)

app.include_router(ai_chat.router)
@app.get("/")
def root():
    return {"message": "Приложение работает!"}
