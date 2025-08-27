import os

BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "localhost")
BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "1883"))
USERNAME    = os.getenv("MQTT_USERNAME", "") or None
PASSWORD    = os.getenv("MQTT_PASSWORD", "") or None
CLIENT_PREFIX = os.getenv("MQTT_CLIENT_PREFIX", "evsim")
QOS = int(os.getenv("MQTT_QOS", "1"))  # 0,1,2

# Simulation defaults
DEFAULT_VEHICLE_ID = os.getenv("EV_VEHICLE_ID", "ev001")
PUBLISH_HZ = float(os.getenv("EV_PUBLISH_HZ", "2.0"))