import datetime
import logging
import os
import string
from random import choices
from traceback import format_exc

from app.config import settings, celery_app, redis_client
from app.logging_config import setup_logging
from fastapi import APIRouter, HTTPException, UploadFile, Form

setup_logging()

logger = logging.getLogger("fastapi")


router = APIRouter(prefix="/api", tags=["API"])

def generate_random_string(length: int) -> str:
    return ''.join(choices(string.ascii_letters, k=length))


@router.post("/upload/")
async def upload_file(file: UploadFile, expiration_minutes: int = Form(...)):
    try:
        # Прочитать загруженный файл
        file_content = await file.read()

        max_file_size = 5 * 1024 * 1024  # 5 МБ в байтах
        if len(file_content) > max_file_size:
            raise HTTPException(status_code=413, detail="Превышен максимальный размер файла (5 МБ).")

        upload_dir = settings.UPLOAD_DIR
        total_size = sum(os.path.getsize(os.path.join(upload_dir, f)) for f in os.listdir(upload_dir) if os.path.isfile(os.path.join(upload_dir, f)))
        max_total_size = 100 * 1024 * 1024  # 100 МБ в байтах
        if total_size + len(file_content) > max_total_size:
            raise HTTPException(status_code=507, detail="Превышен общий лимит размера файлов (100 МБ). Освободите место и повторите попытку.")

        start_file_name = file.filename
        # Сгенерировать уникальное имя файла и ID для удаления
        file_extension = os.path.splitext(file.filename)[1]
        file_id = generate_random_string(12)
        dell_id = generate_random_string(12)

        # Сохранить файл на диск
        file_path = os.path.join(settings.UPLOAD_DIR, file_id + file_extension)
        with open(file_path, "wb") as f:
            f.write(file_content)

        # Рассчитать время истечения в секундах
        expiration_seconds = expiration_minutes * 60
        expiration_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=expiration_seconds)

        # Запланировать задачу для удаления файла после истечения времени
        celery_res = celery_app.send_task('delete_file_scheduled', args=[file_id, dell_id], countdown=expiration_seconds)
        logger.info(f"Задача {celery_res}")
        # # URL-адреса для метаданных
        download_url = f"{settings.BASE_URL}/files/{file_id + file_extension}"
        view_url = f"{settings.BASE_URL}/view_file/{file_id}"

        # Сохранить метаданные в Redis
        redis_key = f"file:{file_id}"  # Уникальный ключ для файла
        redis_client.hmset(redis_key, {"file_path": file_path,
                                       "dell_id": dell_id,
                                       "download_url": download_url,
                                       "expiration_time": int(expiration_time.timestamp()),
                                       "start_file_name": start_file_name})
        logger.info(f"Сохранены метаданные файла {file_id} в Redis\n"
                      f"{redis_client.hget(redis_key, 'file_path')=}")
        return {
            "message": "Файл успешно загружен",
            "file_id": file_id,
            "dell_id": dell_id,
            "download_url": download_url,
            "view_url": view_url,
            "expiration_time": expiration_time.isoformat(),
            "expiration_seconds": expiration_seconds
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Ошибка загрузки файла: {e.__class__.__name__} :\n{format_exc()}")
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки файла: {e.__class__.__name__} :\n{format_exc()}")


@router.delete("/delete/{file_id}/{dell_id}")
async def delete_file(file_id: str, dell_id: str):
    redis_key = f"file:{file_id}"
    file_info = redis_client.hgetall(redis_key)
    logger.info(f"{file_info=}")
    if not file_info:
        raise HTTPException(status_code=404, detail="Файл не найден")

    dell_id_redis = file_info.get(b"dell_id").decode()
    if dell_id_redis != dell_id:
        raise HTTPException(status_code=403, detail="Не совпадает айди удаления с айди удаления файла")

    file_path = file_info.get(b"file_path").decode()

    # Удаление файла и очистка записи в Redis
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Файл {file_path} успешно удален!")
        else:
            logger.warning(f"Файл {file_path} не найден.")

        redis_client.delete(redis_key)
        return {"message": "Файл успешно удален и запись в Redis очищена!"}

    except OSError as e:
        logger.error(f"Error deleting file {file_path}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка удаления файла: {str(e)}")

@router.get("/files")
async def get_files(
        limit=100,
):
    cursor = 0
    keys = []
    while len(keys) < limit:  # Ограничение на 100 записей всего
        cursor, batch = redis_client.scan(cursor, match="files:*", count=100)
        keys.extend(batch)
        if cursor == 0 or len(keys) >= 100:
            break

    # Обрезаем до 100, если набралось больше
    keys = keys[:limit]
    logger.info(f"{keys=}")
    return keys
