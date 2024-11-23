import requests
import time
import sqlite3
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # для импорта config
from config import *
from database import save_humidity_data

class HumidityController:
    def __init__(self):
        self.current_humidity = None

    def get_settings(self):
        """Получение настроек из БД"""
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT max_humidity FROM settings WHERE id = 1")
        settings = c.fetchone()
        conn.close()
        return settings[0] if settings else None

    def check_and_control(self):
        """Проверка условий и управление вытяжкой"""
        try:
            # Получаем данные о влажности
            response = requests.get(f"{SENSOR_URL}/humidity")
            sensor_data = response.json()
            self.current_humidity = sensor_data['humidity']

            # Сохраняем данные в БД при каждом измерении
            save_humidity_data(self.current_humidity)

            max_humidity = self.get_settings()

            # Определяем нужное состояние вытяжки
            if self.current_humidity > max_humidity:
                fan_status = 'ON'
            else:
                fan_status = 'OFF'
                
            print(f"Текущая влажность: {self.current_humidity}, максимальная: {max_humidity}, статус вытяжки: {fan_status}")

            # Обновляем статус вытяжки на датчике
            requests.post(f"{SENSOR_URL}/fan_status", json={'status': fan_status == 'ON'})
            
            # Отправляем команду на управление вытяжкой
            requests.post(f"{FAN_URL}/control", json={'status': fan_status})

        except Exception as e:
            print(f"Ошибка в контроллере: {e}")


if __name__ == "__main__":
    controller = HumidityController()
    try:
        print("Контроллер запущен")
        while True:
            controller.check_and_control()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nКонтроллер остановлен")