FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
# Сначала обновляем pip, затем устанавливаем зависимости, затем ОБЯЗАТЕЛЬНО обновляем redis
RUN pip install --no-cache-dir --upgrade pip && \
    pip uninstall -y redis redis-py 2>/dev/null || true && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir --force-reinstall redis==5.0.0

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
