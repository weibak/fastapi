from fastapi import FastAPI
# Импортируем наш новый модуль с роутером
from app.routers import users
from app.routers import profiles
app = FastAPI(title="My Architecture App")

# Подключаем роутер к главному приложению.
# Это похоже на подключение плагина.
app.include_router(users.router)

app.include_router(profiles.router)

@app.get("/")
def root():
    return {"message": "Приложение работает!"}
