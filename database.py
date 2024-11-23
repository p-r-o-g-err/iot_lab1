import sqlite3
from config import DB_NAME
from utils import hash_password

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Создаем таблицу пользователей
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
    
    # Создаем таблицу настроек
    c.execute('''CREATE TABLE IF NOT EXISTS settings 
                 (id INTEGER PRIMARY KEY, max_humidity REAL)''')
    
    # Создаем таблицу истории влажности
    c.execute('''CREATE TABLE IF NOT EXISTS humidity_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        humidity REAL,
        fan_status TEXT
    )''')

    # Очищаем таблицу истории влажности
    c.execute("DELETE FROM humidity_history")
    
    # Добавляем тестового пользователя (admin/admin)
    hashed_pwd = hash_password("admin")
    c.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)",
             ("admin", hashed_pwd))
    
    # Добавляем начальные настройки
    c.execute("INSERT OR IGNORE INTO settings (max_humidity) VALUES (?)",
             (60.0,))
    
    conn.commit()
    conn.close()

def save_humidity_data(humidity):
    """Сохранение данных о влажности"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # # Удаляем старые записи, оставляем последние 30
    # c.execute('''DELETE FROM humidity_history 
    #              WHERE id NOT IN (
    #                  SELECT id FROM humidity_history 
    #                  ORDER BY timestamp DESC 
    #                  LIMIT 30
    #              )''')
    
    # Добавляем новую запись
    c.execute('''INSERT INTO humidity_history 
                 (humidity) 
                 VALUES (?)''', 
              (humidity,))
    
    conn.commit()
    conn.close()

def get_humidity_history():
    """Получение истории влажности"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Получаем последние 30 записей
    c.execute('''SELECT timestamp, humidity
                 FROM humidity_history 
                 ORDER BY timestamp DESC 
                 LIMIT 30''')
    
    # Преобразуем результаты в список словарей
    history = [
        {
            'timestamp': row[0], 
            'humidity': row[1]
        } for row in c.fetchall()
    ]
    
    conn.close()
    return list(reversed(history))  # Сортируем от старых к новым

def get_settings():
    """Получение максимальной влажности"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT max_humidity FROM settings WHERE id = 1")
    settings = c.fetchone()
    conn.close()
    return settings[0] if settings else 60.0  # Значение по умолчанию