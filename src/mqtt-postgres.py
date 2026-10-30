"""
mqtt-postgres.py
====================================
This is an example of connecting to both MQTT and PostgreSQL
from Python.

| Author: Seth McNeill
| Date: 2026 September 06
"""

import time
import ssl
import paho.mqtt.client as mqtt
import os
from dotenv import load_dotenv
import logging
import psycopg
from datetime import datetime
import argparse
from functools import partial  # for adding arguments to MQTT callbacks


# --- MQTT CALLBACKS ---
def on_connect(client, userdata, flags, rc, properties=None, dbconfig=None, topic=None):
    """Triggered when the client connects to the broker."""
    if rc == 0:
        # print(f"[SUCCESS] Connected to {MQTT_HOST} on port {MQTT_PORT}")
        # print(f"[STATUS]  Subscribing to topic: {MQTT_TOPIC}...")
        print("Successfully connected to MQTT")
        client.subscribe(topic)
    else:
        print(f"[ERROR]   Connection failed with status code: {rc}")
        if rc == 5:
            print("[ERROR]   Check your username or password credentials.")

def on_message(client, userdata, msg, dbconfig_dict, insert_query):
    """Triggered when a message is received from a subscribed topic."""
    print("\n--- NEW MESSAGE RECEIVED ---")
    print(f"Topic:   {msg.topic}")
    print(f"Payload: {msg.payload.decode()}")
    print("----------------------------\n")
    # NEED TO VALIDATE/SECURE INCOMING DATA
    # Submit to database
    try:
        with psycopg.connect(**dbconfig_dict) as conn:
            with conn.cursor() as cur:
                # For a single row:
                cur.execute(insert_query, (msg.payload.decode(),))
                
                # Commit changes to make them permanent
                conn.commit()
                print("Message inserted into database successfully!")
                
    except Exception as e:
        print(f"An error occurred inserting to database: {e}")

def on_publish(client, userdata, mid, reason_code=None, properties=None):
    """Triggered when a message is successfully published."""
    print("[SUCCESS] Message successfully sent to the broker.")


def main():
    # 1. Define  the database connection details
    dbconfig_dict = {
        "dbname": os.getenv('DBNAME'),
        "user": os.getenv('DBUSER'),
        "password": os.getenv('DBPASS'),
        "host": os.getenv("DBHOST"),
        "port": os.getenv("DBPORT")
    }
    # --- MQTT CONFIGURATION ---
    MQTT_HOST = os.getenv('MQTT_HOST')
    MQTT_PORT = int(os.getenv('MQTT_PORT'))
    MQTT_PATH = os.getenv('MQTT_PATH') 
    # MQTT_TOPIC = "test/websocket/channel"
    MQTT_TOPIC = os.getenv('MQTT_TOPIC')

    # --- MQTT AUTHENTICATION ---
    MQTT_USER = os.getenv('MQTT_USER')
    MQTT_PASS = os.getenv('MQTT_PASS')

    # 2. Define the SQL template using %s placeholders
    insert_query = psycopg.sql.SQL("""
        INSERT INTO {table} ({field}) 
        VALUES (%s);
    """).format(table=psycopg.sql.Identifier(os.getenv('DBTABLE')), 
           field=psycopg.sql.Identifier(os.getenv('DBCOL')),
           )
    # Initialize client with WebSockets transport layer
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2, transport="websockets")  
    logging.basicConfig(level=logging.DEBUG)
    client.enable_logger()    

    # Configure credentials 
    client.username_pw_set(username=MQTT_USER, password=MQTT_PASS)
    
    # Configure WebSocket path
    client.ws_set_options(
          path=MQTT_PATH
    )
#    client.ws_set_options(
#          path=MQTT_PATH,
#	  headers={
#            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
#            "Accept-Language": "en-US,en;q=0.9"
#        }
#    )
    
    # Configure TLS/SSL for secure 'wss' connection
    client.tls_set(cert_reqs=ssl.CERT_REQUIRED)

    # Assign event callbacks
    # create a callback with the expected arguments while adding needed ones
    bound_on_connect = partial(on_connect, dbconfig=dbconfig_dict, topic=MQTT_TOPIC)
    client.on_connect = bound_on_connect
    # create a callback with the expected arguments while adding needed ones
    bound_on_message = partial(on_message, dbconfig_dict=dbconfig_dict, insert_query=insert_query)
    client.on_message = bound_on_message
    client.on_publish = on_publish

    print(f"[STATUS]  Initiating connection to wss://{MQTT_HOST}:{MQTT_PORT}{MQTT_PATH}...")
    
    try:
        client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
    except Exception as e:
        print(f"[ERROR]   Failed to initiate network connection: {e}")
        return

    # Start the network loop in the background
    client.loop_start()

    # Wait briefly for the connection and subscription to establish
    time.sleep(2)

    # Publish a test message
    curTime = datetime.now()
    timeString = curTime.strftime("%Y-%m-%d %H:%M:%S")
    test_payload = f'{{"ModName":"MQTT2Postgres","date":"{timeString}","boot":"True"}}'
    print(f"[STATUS]  Publishing message: '{test_payload}'")
    client.publish(MQTT_TOPIC, test_payload, qos=1)

    # Keep the script alive to receive the message back
    try:
        print("[STATUS]  Listening for incoming echo messages. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[STATUS]  Stopping script...")
    finally:
        client.loop_stop()
        client.disconnect()
        print("[STATUS]  Disconnected cleanly.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A MQTT to PostgreSQL database connector")
    parser.add_argument("-f", "--filename", help="Name of the env file with all the settings")
    args = parser.parse_args()
    load_dotenv(args.filename)

    main()
