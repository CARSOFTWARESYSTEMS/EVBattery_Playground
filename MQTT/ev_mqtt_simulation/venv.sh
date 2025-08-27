# 1) Set up env
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2) (Optional) Configure env vars
# export MQTT_BROKER_HOST=localhost
export MQTT_BROKER_HOST=test.mosquitto.org
export MQTT_BROKER_PORT=1883
export MQTT_USERNAME=
export MQTT_PASSWORD=
export MQTT_CLIENT_PREFIX=evsim
export MQTT_QOS=1
export EV_VEHICLE_ID=ev001

# 3) Run a broker (Docker Mosquitto example)
docker run -it --rm -p 1883:1883 eclipse-mosquitto

# 4) In new terminals, start subscribers
python subscribers/subscriber_android_ui.py
python subscribers/subscriber_ai_predictor.py
python subscribers/subscriber_other_sensors.py

# 5) Start the publisher
python publisher/publisher_ev_bms.py --hz 2 --vehicle ev001
