import time
import random
import paho.mqtt.client as mqtt
import threading
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # для импорта config
from config import *

class HumiditySensor:
    """Симулятор датчика влажности"""
    def __init__(self):
        self.client = mqtt.Client("humidity_sensor")
        self.client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
        self.current_humidity = 50.0
        
        # Подписываемся на состояние вытяжки
        self.client.on_message = self.on_message
        self.client.subscribe(MQTT_TOPIC_FAN)
        
        self.fan_is_active = False
        self.client.loop_start()
    
    def on_message(self, client, userdata, msg):
        """Отслеживаем состояние вытяжки"""
        command = msg.payload.decode()
        self.fan_is_active = (command == "ON")
    
    def simulate(self):
        """Одно измерение влажности"""
        # Базовое случайное изменение
        natural_change = random.uniform(-2, 3)
        
        # Эффект от работы вытяжки
        fan_effect = random.uniform(-3, -2) if self.fan_is_active else 0
        
        # Суммарное изменение
        self.current_humidity += natural_change + fan_effect
        self.current_humidity = max(0, min(80, self.current_humidity))
        
        # Публикация значения влажности
        self.client.publish(MQTT_TOPIC_HUMIDITY, f"{self.current_humidity:.1f}")
        print(f"Текущая влажность: {self.current_humidity:.1f}% " + 
                f"(Вытяжка: {'Вкл' if self.fan_is_active else 'Выкл'})")
        time.sleep(2)

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()


class ExhaustFan:
    """Симулятор вытяжки"""
    def __init__(self):
        self.client = mqtt.Client("exhaust_fan")
        self.client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
        self.is_active = False
        
        # Подписка на команды управления
        self.client.on_message = self.on_message
        self.client.subscribe(MQTT_TOPIC_FAN)
        self.client.loop_start()
    
    def on_message(self, client, userdata, msg):
        """Обработка команд включения/выключения"""
        command = msg.payload.decode()
        self.is_active = (command == "ON")
        print(f"Состояние вытяжки изменено на: {'ON' if self.is_active else 'OFF'}")

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()

def run_sensor(sensor):
    try:
        print("Запуск симуляции датчика влажности")
        while True:
            sensor.simulate()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nОстановка симуляции датчика влажности")
        sensor.stop()

def run_fan(fan):
    try:
        print("Запуск симулятора вытяжки")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nОстановка симулятора вытяжки")
        fan.stop()

if __name__ == "__main__":
    sensor = HumiditySensor()
    fan = ExhaustFan()
    
    # Запуск в отдельных потоках
    sensor_thread = threading.Thread(target=run_sensor, args=(sensor,))
    fan_thread = threading.Thread(target=run_fan, args=(fan,))
    
    sensor_thread.start()
    fan_thread.start()

    try:
        sensor_thread.join()
        fan_thread.join()
    except KeyboardInterrupt:
        print("\nОстановка симуляции")
