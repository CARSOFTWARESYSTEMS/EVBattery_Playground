#!/usr/bin/env python3
# AI-like predictor subscriber: simple rule-based alerts using core + other sensors.

import json
import os
from paho.mqtt import client as mqtt
import mqtt_config as cfg

VEHICLE = os.getenv("EV_VEHICLE_ID", cfg.DEFAULT_VEHICLE_ID)

state = {
    "voltage": None,
    "current": None,
    "temperature": None,
    "soc": None,
    "soh": None,
    "speed": None,
    "ambient_temperature": None,
    "gps": None,
}

def on_connect(client, userdata, flags, rc):
    print(f"[ai] Connected with result code {rc}")
    base = f"ev/{VEHICLE}"
    topics = [
        (f"{base}/bms/voltage", cfg.QOS),
        (f"{base}/bms/current", cfg.QOS),
        (f"{base}/bms/temperature", cfg.QOS),
        (f"{base}/sensors/soc", cfg.QOS),
        (f"{base}/sensors/soh", cfg.QOS),
        (f"{base}/sensors/speed", cfg.QOS),
        (f"{base}/sensors/ambient_temperature", cfg.QOS),
        (f"{base}/sensors/gps", cfg.QOS),
        (f"{base}/telemetry", cfg.QOS),
    ]
    client.subscribe(topics)

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode("utf-8", errors="ignore")
    leaf = topic.split("/")[-1]

    try:
        if leaf in ("voltage", "current", "temperature", "soc", "soh", "speed", "ambient_temperature"):
            state[leaf] = float(payload)
        elif leaf == "gps":
            state["gps"] = json.loads(payload)
        elif leaf == "telemetry":
            data = json.loads(payload)
            for k in ("voltage","current","temperature","soc","soh","speed","ambient_temperature","gps"):
                if k in data:
                    state[k] = data[k]
    except Exception as e:
        print(f"[ai] Parse error on {topic}: {e}")

    evaluate()

def evaluate():
    v = state["voltage"]
    c = state["current"]
    t = state["temperature"]
    soc = state["soc"]
    soh = state["soh"]
    amb = state["ambient_temperature"]

    alerts = []

    if t is not None and t > 55:
        alerts.append("🔥 High battery temp risk")
    if c is not None and abs(c) > 80:
        alerts.append("⚡ Overcurrent danger")
    if v is not None and v < 42.0 and (soc is None or soc < 15):
        alerts.append("🔋 Low voltage / SOC — charge soon")
    if amb is not None and t is not None and (t - amb) > 25:
        alerts.append("🌡️ Thermal runaway suspicion")

    if alerts:
        print(f"\n[ai] Alerts: {', '.join(alerts)}")
    else:
        print(".", end="", flush=True)  # heartbeat

def main():
    client_id = f"{cfg.CLIENT_PREFIX}-sub-ai-{VEHICLE}"
    client = mqtt.Client(client_id=client_id, clean_session=True)
    if cfg.USERNAME and cfg.PASSWORD:
        client.username_pw_set(cfg.USERNAME, cfg.PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(cfg.BROKER_HOST, cfg.BROKER_PORT, keepalive=30)
    client.loop_forever()

if __name__ == "__main__":
    main()