import os
import sqlite3

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv

# Load the variables from the .env file into the system environment
load_dotenv()

# Важно: используем префикс sqlite+aiosqlite для асинхронной работы
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL") or ""

def get_db_connection():
    conn = sqlite3.connect(os.getenv("DATABASE_NAME") or "")
    conn.row_factory = sqlite3.Row
    return conn

# 1. Создаем асинхронный движок (Async Engine)
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False} # Нужно только для SQLite
)

# 2. Создаем фабрику асинхронных сессий.
# expire_on_commit=False — важная настройка для async, чтобы объекты не "протухали" после комита.
AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# 3. Базовый класс для моделей (современный синтаксис SQLAlchemy 2.0)
class Base(DeclarativeBase):
    pass

# 4. Dependency (Зависимость).
# Это асинхронный генератор.
async def get_db():
    # Используем async with — это гарантирует, что сессия закроется корректно
    async with AsyncSessionLocal() as db:
        yield db


def create_application_logs():
    conn = get_db_connection()
    conn.execute("""CREATE TABLE IF NOT EXISTS application_logs
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     session_id TEXT,
                     user_query TEXT,
                     gpt_response TEXT,
                     model TEXT,
                     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    conn.close()



def create_document_store():
    conn = get_db_connection()
    conn.execute("""CREATE TABLE IF NOT EXISTS document_store
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     filename TEXT,
                     upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    conn.close()


def insert_application_logs(session_id, user_query, gpt_response, model):
    conn = get_db_connection()
    conn.execute('INSERT INTO application_logs (session_id, user_query, gpt_response, model) VALUES (?, ?, ?, ?)',
                 (session_id, user_query, gpt_response, model))
    conn.commit()
    conn.close()

def get_chat_history(session_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_query, gpt_response FROM application_logs WHERE session_id = ? ORDER BY created_at', (session_id,))
    messages = []
    for row in cursor.fetchall():
        messages.extend([
            {"role": "human", "content": row['user_query']},
            {"role": "ai", "content": row['gpt_response']}
        ])
    conn.close()
    return messages

def insert_document_record(filename):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO document_store (filename) VALUES (?)', (filename,))
    file_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return file_id

def delete_document_record(file_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM document_store WHERE id = ?', (file_id,))
    conn.commit()
    conn.close()
    return True

def get_all_documents():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, filename, upload_timestamp FROM document_store ORDER BY upload_timestamp DESC')
    documents = cursor.fetchall()
    conn.close()
    return [dict(doc) for doc in documents]
