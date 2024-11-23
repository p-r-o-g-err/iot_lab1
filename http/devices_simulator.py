from flask import Flask, request, jsonify
import random
import time
import threading

app_sensor = Flask(__name__)
app_fan = Flask(__name__)

class HumiditySensor:
    def __init__(self):
        self.current_humidity = 50.0
        self.fan_is_active = False

    def simulate(self):
        # Базовое случайное изменение
        natural_change = random.uniform(-2, 3)
        # Эффект от работы вытяжки
        fan_effect = random.uniform(-3, -2) if self.fan_is_active else 0
        # Суммарное изменение
        self.current_humidity += natural_change + fan_effect
        self.current_humidity = max(0, min(80, self.current_humidity))
        
        return round(self.current_humidity, 1)

@app_sensor.route('/humidity', methods=['GET'])
def get_humidity():
    global sensor
    return jsonify({
        'humidity': sensor.simulate(),
        'fan_status': 'ON' if sensor.fan_is_active else 'OFF'
    })

@app_sensor.route('/fan_status', methods=['POST'])
def set_fan_status():
    global sensor
    sensor.fan_is_active = request.json.get('status', False)
    return jsonify({'status': 'success'})

@app_fan.route('/control', methods=['POST'])
def control_fan():
    status = request.json.get('status', 'OFF')
    return jsonify({'status': status})

def run_sensor_app():
    app_sensor.run(port=5001)

def run_fan_app():
    app_fan.run(port=5002)

if __name__ == "__main__":
    sensor = HumiditySensor()
    
    # Запуск серверов в отдельных потоках
    sensor_thread = threading.Thread(target=run_sensor_app)
    fan_thread = threading.Thread(target=run_fan_app)
    sensor_thread.start()
    fan_thread.start()

    sensor_thread.join()
    fan_thread.join()

    print("Запущены симуляторы устройств")