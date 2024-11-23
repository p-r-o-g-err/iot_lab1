DB_NAME = "humidity_control.db"
SECRET_KEY = "secret-key"
# Настройки для MQTT
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_USERNAME = "test_username"
MQTT_PASSWORD = "test_password"
MQTT_TOPIC_HUMIDITY = "room/humidity"
MQTT_TOPIC_FAN = "room/fan"
# Настройки для HTTP
SENSOR_URL = "http://localhost:5001"  # URL симулятора датчика
FAN_URL = "http://localhost:5002"     # URL симулятора вытяжки