import argparse
import locale
import logging
import requests
import paho.mqtt.publish as mqtt_publish
import paho.mqtt.client as mqtt_client
import json
import time
import sys

from google.cloud.speech import enums
from google.cloud.speech import types

from myd_tts_pi import myd_tts_speak

def on_connect(mqtt_client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() - if we lose the connection and
    # reconnect then subscriptions will be renewed.
    mqtt_client.subscribe("mydaemon/speak")


# The callback for when a PUBLISH message is received from the server.
def on_message(mqtt_client, userdata, msg):

    # check to see if the message has valid JSON content
    message_text = msg.payload.decode('utf-8')
    try:
        message_json = json.loads(message_text)
    except Exception as e:
        print("Couldn't parse raw data: %s" % message_text, e)
    else:
        print("JSON received : ", message_json)

    if message_json["utterance"] != None:
        
        # publish speaking status to general
        publish_json = {"speaking": True}
        publish_string = json.dumps(publish_json)
        mqtt_publish.single("mydaemon/general", publish_string, hostname="test.mosquitto.org")
        # print the JSON
        print("JSON published: ", publish_json)
                
        myd_tts_speak(message_json["utterance"])
        
        # publish speaking status to general
        publish_json = {"speaking": False}
        publish_string = json.dumps(publish_json)
        mqtt_publish.single("mydaemon/general", publish_string, hostname="test.mosquitto.org")
        # print the JSON
        print("JSON published: ", publish_json)
                

def main():
    # Create an MQTT client and attach our routines to it.
    local_mqtt_client = mqtt_client.Client()
    local_mqtt_client.on_connect = on_connect
    local_mqtt_client.on_message = on_message
    local_mqtt_client.connect("test.mosquitto.org", 1883, 60)

    while True:
        # Wait for the question generator
        local_mqtt_client.loop_forever()


if __name__ == '__main__':
    main()


