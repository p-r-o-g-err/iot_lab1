import paho.mqtt.client as mqtt
import sqlite3
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # для импорта config
from config import *

class HumidityController:
    def __init__(self):
        self.client = mqtt.Client("humidity_controller")
        self.client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        self.client.connect(MQTT_BROKER, MQTT_PORT)
        
        # Подписываемся на топик с данными датчика
        self.client.on_message = self.on_message
        self.client.subscribe(MQTT_TOPIC_HUMIDITY)
        
        self.current_humidity = None
        self.client.loop_start()
        
    def get_settings(self):
        """Получение настроек из БД"""
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT max_humidity FROM settings WHERE id = 1")
        settings = c.fetchone()
        conn.close()
        return settings[0] if settings else None
    
    def on_message(self, client, userdata, msg):
        """Обработка входящих сообщений"""
        try:
            if msg.topic == MQTT_TOPIC_HUMIDITY:
                # Получили новые данные от датчика
                self.current_humidity = float(msg.payload.decode())
                self.check_and_control()
                
        except Exception as e:
            print(f"Error processing message: {e}")

    def check_and_control(self):
        """Проверка условий и управление вытяжкой"""
        if self.current_humidity is None:
            return
            
        max_humidity = self.get_settings()
        
        print(f"Текущая влажность: {self.current_humidity}, максимальная: {max_humidity}")
        
        # Определяем нужное состояние вытяжки
        if self.current_humidity > max_humidity:
            self.client.publish(MQTT_TOPIC_FAN, "ON")
        else:
            self.client.publish(MQTT_TOPIC_FAN, "OFF")

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()


if __name__ == "__main__":
    controller = HumidityController()
    try:
        print("Контроллер запущен")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nКонтроллер остановлен")
    finally:
        controller.stop()