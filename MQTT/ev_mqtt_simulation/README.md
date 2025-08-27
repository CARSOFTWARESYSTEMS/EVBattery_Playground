# EV MQTT Simulation (Publishers & Subscribers)

This mini-project lets you simulate an EV Battery Management System (BMS) publisher and multiple subscribers:
- **Publisher**: Publishes Voltage, Current, Temperature, and other EV sensor data.
- **Subscriber (Android-UI-like)**: Subscribes to Voltage/Current/Temperature and prints a compact UI in the console.
- **Subscriber (AI Predictor)**: Subscribes to the same core metrics + other sensors and prints simple rule-based "predictions".
- **Subscriber (Other Sensors)**: Subscribes to a wildcard path for all other EV sensor topics.

You can use any MQTT broker you like (local Mosquitto, public test broker, etc.).
All scripts are configurable via environment variables or `mqtt_config.py` defaults.

---

## Quick Start

1) **Install deps**
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

2) **Set (optional) environment overrides**
```bash


export MQTT_BROKER_HOST=test.mosquitto.org
export MQTT_BROKER_PORT=1883
export MQTT_USERNAME=
export MQTT_PASSWORD=
export MQTT_CLIENT_PREFIX=evsim
export MQTT_QOS=1
export EV_VEHICLE_ID=ev001



```

3) **Run a broker (option A: local Mosquitto via Docker)**
```bash

brew install --cask docker

open -a Docker
docker run -it --rm -p 1883:1883 eclipse-mosquitto

```

4) **Start the subscribers (in separate shells)**
```bash

# Terminal A — Android UI subscriber
export PYTHONPATH="$PWD"
export MQTT_BROKER_HOST=test.mosquitto.org
export MQTT_BROKER_PORT=1883
python subscribers/subscriber_android_ui.py


# Terminal B — AI predictor subscriber
export PYTHONPATH="$PWD"
export MQTT_BROKER_HOST=test.mosquitto.org
export MQTT_BROKER_PORT=1883
python subscribers/subscriber_ai_predictor.py


# Terminal C — Other-sensors subscriber
export PYTHONPATH="$PWD"
export MQTT_BROKER_HOST=test.mosquitto.org
export MQTT_BROKER_PORT=1883
python subscribers/subscriber_other_sensors.py


```

5) **Start the publisher**
```bash

# Terminal D — Publisher
export PYTHONPATH="$PWD"
export MQTT_BROKER_HOST=test.mosquitto.org
export MQTT_BROKER_PORT=1883
python publisher/publisher_ev_bms.py --hz 2 --vehicle ev001




```

---

## Topic Structure

- Core BMS telemetry (JSON blob):
  - `ev/<vehicleId>/telemetry`
- Individual sensor topics (primitive values):
  - `ev/<vehicleId>/bms/voltage` (Volts)
  - `ev/<vehicleId>/bms/current` (Amps, +ve=discharge)
  - `ev/<vehicleId>/bms/temperature` (°C)
- Other sensor topics (primitive JSON or numbers):
  - `ev/<vehicleId>/sensors/speed` (km/h)
  - `ev/<vehicleId>/sensors/soc`   (%)
  - `ev/<vehicleId>/sensors/soh`   (%)
  - `ev/<vehicleId>/sensors/gps`   (JSON: {"lat":..,"lon":..})
  - `ev/<vehicleId>/sensors/ambient_temperature` (°C)

---

## Using Postman as a simulator

Postman (v10+) can connect to MQTT brokers.

- Create a new **MQTT** request.
- **Broker URL**: `mqtt://test.mosquitto.org:1883` (or your broker or mqtt://localhost:1883)
- **Client ID**: e.g. `postman-evsim-1`
- **Username/Password**: if your broker requires it.
- **SUBSCRIBE** to one or more:
  - `ev/+/bms/+`
  - `ev/+/sensors/#`
  - `ev/+/telemetry`
- **PUBLISH** test messages:
  - Topic: `ev/ev001/bms/voltage`, Payload: `51.7`
  - Topic: `ev/ev001/bms/current`, Payload: `12.3`
  - Topic: `ev/ev001/bms/temperature`, Payload: `32.5`
  - Topic: `ev/ev001/sensors/gps`, Payload: `{"lat":12.97,"lon":77.59}`
  - Topic: ev/ev001/sensors/#
  - Topic: ev/ev001/telemetry

You should immediately see your subscribers react.

---

## Notes
- All scripts handle reconnects and will print errors if the broker is unavailable.
- The AI predictor here is intentionally simple (rule-based thresholds). Replace with your own ML easily.
- QoS is configurable via env or config (default 1).
- All scripts are cross-platform and tested with Python 3.10+.



# Other installations
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install mosquitto

echo 'export PATH="/opt/homebrew/sbin:$PATH"' >> ~/.zshrc
source ~/.zshrc

cat > ~/mosquitto.conf <<'EOF'
listener 1883 127.0.0.1
allow_anonymous true
persistence false
log_type all
EOF

# Stop any background instance just in case
brew services stop mosquitto 2>/dev/null || true

# Start broker with verbose logs
mosquitto -c ~/mosquitto.conf -v

# Testing - Subscriber
mosquitto_sub -h 127.0.0.1 -t 'test/topic' -v

# Testing - Publisher
mosquitto_pub -h 127.0.0.1 -t 'test/topic' -m 'hello'
