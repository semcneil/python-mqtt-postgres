# python-mqtt-postgres
This shows connecting MQTT subscription to save in a PostgreSQL database

Install the needed libraries
```
uv pip install paho-mqtt dotenv psycopg
```

To run in the background and survive terminal disconnects use `tmux`
```
tmux new -s mqttpost # starts new session named mqttpost
python src/mqtt-postgres.py  # starts script
```
Detach by pressing `Ctrl + b` then `d`

Reconnect later in another terminal with
```
tmux attach -t mqttpost
```

This assumes an environmental variable file in the form
```
# --- Database ---
DBNAME="database_name"
DBUSER="database_username"
DBPASS="database_password"
DBHOST="localhost"
DBPORT="5432"
DBTABLE="mydatatablename"
DBCOL="datacolumnname"

# --- MQTT ---
MQTT_HOST="mqtt.host.name"
MQTT_PORT="443"
MQTT_PATH="/mqtt"
MQTT_TOPIC="nesso/test"
MQTT_USER="mqtt_user"
MQTT_PASS="mqtt_pass"
```
Stored in a location such as: `/etc/iot-creds/vars.sh`
