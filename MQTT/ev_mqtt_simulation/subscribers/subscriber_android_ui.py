#!/usr/bin/env python3
# Android-like UI subscriber: prints compact live tiles for Voltage/Current/Temperature.

import os
from paho.mqtt import client as mqtt
import mqtt_config as cfg

VEHICLE = os.getenv("EV_VEHICLE_ID", cfg.DEFAULT_VEHICLE_ID)

state = {"voltage": None, "current": None, "temperature": None}

def on_connect(client, userdata, flags, rc):
    print(f"[ui] Connected with result code {rc}")
    base = f"ev/{VEHICLE}/bms"
    client.subscribe([(f"{base}/voltage", cfg.QOS),
                      (f"{base}/current", cfg.QOS),
                      (f"{base}/temperature", cfg.QOS)])

def on_message(client, userdata, msg):
    t = msg.topic.rsplit("/", 1)[-1]
    payload = msg.payload.decode("utf-8", errors="ignore")
    if t in state:
        try:
            state[t] = float(payload)
        except ValueError:
            state[t] = payload
        render()

def render():
    v = state["voltage"]
    c = state["current"]
    temp = state["temperature"]
    v_str = "None" if v is None else f"{v:6.2f}"
    c_str = "None" if c is None else f"{c:6.2f}"
    t_str = "None" if temp is None else f"{temp:5.2f}"
    print(f"\r[UI]  Voltage: {v_str} V  |  Current: {c_str} A  |  Temp: {t_str} °C", end="", flush=True)

def main():
    client_id = f"{cfg.CLIENT_PREFIX}-sub-ui-{VEHICLE}"
    client = mqtt.Client(client_id=client_id, clean_session=True)
    if cfg.USERNAME and cfg.PASSWORD:
        client.username_pw_set(cfg.USERNAME, cfg.PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(cfg.BROKER_HOST, cfg.BROKER_PORT, keepalive=30)
    client.loop_forever()

if __name__ == "__main__":
    main()