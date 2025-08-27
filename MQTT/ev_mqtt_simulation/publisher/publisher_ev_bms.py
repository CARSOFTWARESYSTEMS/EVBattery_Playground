#!/usr/bin/env python3
# EV BMS Publisher: publishes Voltage/Current/Temperature and other sensors.

import json
import math
import random
import signal
import time
import argparse
from typing import Dict
from paho.mqtt import client as mqtt
import mqtt_config as cfg

RUN = True

def handle_signal(signum, frame):
    global RUN
    print("\n[publisher] Caught signal, stopping...", flush=True)
    RUN = False

signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)

def make_client(client_id: str) -> mqtt.Client:
    c = mqtt.Client(client_id=client_id, clean_session=True, protocol=mqtt.MQTTv311)
    if cfg.USERNAME and cfg.PASSWORD:
        c.username_pw_set(cfg.USERNAME, cfg.PASSWORD)
    c.enable_logger()
    return c

def connect(client: mqtt.Client):
    client.connect(cfg.BROKER_HOST, cfg.BROKER_PORT, keepalive=30)

def publish(client: mqtt.Client, topic: str, payload, retain=False):
    result = client.publish(topic, payload=payload, qos=cfg.QOS, retain=retain)
    status = result[0]
    if status != mqtt.MQTT_ERR_SUCCESS:
        print(f"[publisher] Failed to publish {topic} (err={status})", flush=True)

def gen_telemetry(t: float) -> Dict:
    # Reasonable synthetic signals
    voltage = 50.0 + 2.0*math.sin(0.2*t) + random.uniform(-0.3, 0.3)
    current = 10.0 + 5.0*math.sin(0.35*t + 0.7) + random.uniform(-0.5, 0.5)  # +ve ~ discharge
    temperature = 30.0 + 5.0*math.sin(0.05*t + 1.3) + random.uniform(-0.4, 0.4)

    soc = max(0.0, min(100.0, 80.0 + 10.0*math.sin(0.01*t)))
    soh = 95.0 + 0.4*math.sin(0.005*t)
    speed = max(0.0, 40.0 + 10.0*math.sin(0.1*t + 0.2))
    ambient = 27.0 + 2.0*math.sin(0.03*t)

    lat = 12.9716 + 0.001*math.sin(0.002*t)
    lon = 77.5946 + 0.001*math.cos(0.002*t)

    return {
        "voltage": round(voltage, 2),
        "current": round(current, 2),
        "temperature": round(temperature, 2),
        "soc": round(soc, 1),
        "soh": round(soh, 1),
        "speed": round(speed, 1),
        "ambient_temperature": round(ambient, 1),
        "gps": {"lat": round(lat, 6), "lon": round(lon, 6)},
        "ts": time.time()
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--vehicle", default=cfg.DEFAULT_VEHICLE_ID, help="Vehicle ID (topic segment)")
    parser.add_argument("--hz", type=float, default=cfg.PUBLISH_HZ, help="Publish rate (messages per second)")
    args = parser.parse_args()

    client_id = f"{cfg.CLIENT_PREFIX}-pub-{args.vehicle}"
    client = make_client(client_id)
    connect(client)
    client.loop_start()

    base = f"ev/{args.vehicle}"
    period = 1.0 / max(0.1, args.hz)
    print(f"[publisher] Publishing to {cfg.BROKER_HOST}:{cfg.BROKER_PORT} at {args.hz} Hz for vehicle '{args.vehicle}'", flush=True)

    t0 = time.time()
    while RUN:
        t = time.time() - t0
        d = gen_telemetry(t)

        # JSON blob
        publish(client, f"{base}/telemetry", json.dumps(d))

        # Individual topics (primitive)
        publish(client, f"{base}/bms/voltage", str(d["voltage"]))
        publish(client, f"{base}/bms/current", str(d["current"]))
        publish(client, f"{base}/bms/temperature", str(d["temperature"]))

        # Other sensors
        publish(client, f"{base}/sensors/speed", str(d["speed"]))
        publish(client, f"{base}/sensors/soc", str(d["soc"]))
        publish(client, f"{base}/sensors/soh", str(d["soh"]))
        publish(client, f"{base}/sensors/ambient_temperature", str(d["ambient_temperature"]))
        publish(client, f"{base}/sensors/gps", json.dumps(d["gps"]))

        time.sleep(period)

    client.loop_stop()
    client.disconnect()
    print("[publisher] Stopped.")

if __name__ == "__main__":
    main()