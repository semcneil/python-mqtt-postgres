# python-mqtt-postgres
This shows connecting MQTT subscription to save in a PostgreSQL database

This assumes an environmental variable file in the form
```
# --- Database ---
DBNAME="database_name"
DBUSER="database_username"
DBPASS="database_password"
DBHOST="localhost"
DBPORT="5432"

# --- MQTT ---
MQTT_HOST="mqtt.host.name"
MQTT_PORT="443"
MQTT_PATH="/mqtt"
MQTT_TOPIC="nesso/test"
MQTT_USER="mqtt_user"
MQTT_PASS="mqtt_pass"
```