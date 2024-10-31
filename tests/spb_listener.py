import time
import json
import os
from mqtt_spb_wrapper import *

_DEBUG = True  # Enable debug messages

print("--- Sparkplug B example - Application Entity Listener")


def callback_app_message(topic, payload):
    print("APP received MESSAGE: %s - %s" % (topic, payload))


def callback_app_command(payload):
    print("APP received CMD: %s" % payload)

# Create the spB entity object
# script_dir = os.path.dirname(os.path.realpath(__file__))
# config_path = os.path.join(script_dir, 'config.json')
# with open(config_path, 'r') as file:
#     config = json.load(file)
# mqtt_config = config.get('mqtt')


group_name =  'haas-test-5'
edge_node_name = 'HAAS-UMC750'
device_name = 'HAAS-UMC750'
mqtt_host = '128.237.92.30'
mqtt_port = int('1883')
mqtt_user = 'admin'
mqtt_pass = 'CMUmfi2024!'
mqtt_tls_enabled = False


app = MqttSpbEntityApplication(group_name, edge_node_name, debug_info=_DEBUG)

# Set callbacks
app.on_message = callback_app_message
app.on_command = callback_app_command

# Set the device Attributes, Data and Commands that will be sent on the DBIRTH message --------------------------

# Attributes
app.attributes.set_value("description", "Test application")

# Commands
app.commands.set_value("rebirth", False)

# Connect to the broker----------------------------------------------------------------
_connected = False
while not _connected:
    print("Trying to connect to broker...")
    _connected = app.connect(mqtt_host, mqtt_port, mqtt_user, mqtt_pass, mqtt_tls_enabled)
    if not _connected:
        print("  Error, could not connect. Trying again in a few seconds ...")
        time.sleep(3)

# Send birth message
app.publish_birth()


# Loop forever, messages and commands will be handeled by the callbacks
while True:
    time.sleep(1000)
