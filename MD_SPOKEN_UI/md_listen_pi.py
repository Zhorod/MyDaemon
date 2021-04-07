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

from md_stt_pi import md_stt_capture

speaking = False

def on_connect(mqtt_client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    
    # Subscribing in on_connect() - if we lose the connection and
    # reconnect then subscriptions will be renewed.
    mqtt_client.subscribe("mydaemon/general")

# The callback for when a PUBLISH message is received from the server.
def on_message(mqtt_client, userdata, msg):

    # check to see if the message has valid JSON content
    # check to see if the message has valid JSON content
    global speaking
    
    message_text = msg.payload.decode('utf-8')
    try:
        message_json = json.loads(message_text)
    except Exception as e:
        print("Couldn't parse raw data: %s" % message_text, e)
    else:
        print("JSON received : ", message_json)

    if message_json["speaking"] != None:
        speaking = message_json["speaking"]
        print("The status of speaking has changed to: ", speaking)
        
def listen():
    global speaking
    while True:
        if speaking == True:
            time.sleep(0.2)
        else:
            utterance = md_stt_capture()
            print("Captured: ", utterance)
            if utterance != None:
                # The utternace has data in it
                # Add the utterance to the JSON
                speaking = True
                message_json = {"user": utterance, "mydaemon": ""}
                message_string = json.dumps(message_json)
                
                # publish the JSON
                mqtt_publish.single("mydaemon/user", message_string, hostname="test.mosquitto.org")
                
                # print the JSON
                print("JSON published: ", message_json)
                
                # check for a shutdown command
                if utterance.lower() == "shutdown" or utterance.lower() == "shut down":
                    sys.exit()
    

def main():
    # Create an MQTT client and attach our routines to it.
    local_mqtt_client = mqtt_client.Client()
    local_mqtt_client.on_connect = on_connect
    local_mqtt_client.on_message = on_message
    local_mqtt_client.connect("test.mosquitto.org", 1883, 60)
    local_mqtt_client.loop_start()

    listen()
    
    local_mqtt_client.loop_stop()
    


if __name__ == '__main__':
    main()

