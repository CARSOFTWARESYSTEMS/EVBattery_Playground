#!/usr/bin/env python3
# Wildcard subscriber for all other EV sensors under `ev/<vehicleId>/sensors/#`.

import os
from paho.mqtt import client as mqtt
import mqtt_config as cfg

VEHICLE = os.getenv("EV_VEHICLE_ID", cfg.DEFAULT_VEHICLE_ID)

def on_connect(client, userdata, flags, rc):
    print(f"[sensors] Connected with result code {rc}")
    client.subscribe((f"ev/{VEHICLE}/sensors/#", cfg.QOS))

def on_message(client, userdata, msg):
    print(f"[sensors] {msg.topic} = {msg.payload.decode('utf-8', errors='ignore')}")

def main():
    client_id = f"{cfg.CLIENT_PREFIX}-sub-sensors-{VEHICLE}"
    client = mqtt.Client(client_id=client_id, clean_session=True)
    if cfg.USERNAME and cfg.PASSWORD:
        client.username_pw_set(cfg.USERNAME, cfg.PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(cfg.BROKER_HOST, cfg.BROKER_PORT, keepalive=30)
    client.loop_forever()

if __name__ == "__main__":
    main()