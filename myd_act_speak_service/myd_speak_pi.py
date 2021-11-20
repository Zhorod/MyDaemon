import argparse
import locale
import logging
import requests
import paho.mqtt.client as mqtt
import json
import time
import sys

from google.cloud.speech import enums
from google.cloud.speech import types

from subprocess import call

from myd_tts_pi import myd_tts_speak


def on_connect(mqtt_client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() - if we lose the connection and
    # reconnect then subscriptions will be renewed.
    mqtt_client.subscribe("mydaemon/speak")
    mqtt_client.subscribe("mydaemon/general")


# The callback for when a PUBLISH message is received from the server.
def on_message(mqtt_client, userdata, msg):
    # check to see if the message has valid JSON content
    message_text = msg.payload.decode('utf-8')
    try:
        message_json = json.loads(message_text)
    except Exception as e:
        print("Couldn't parse raw data: %s" % message_text, e)
    else:
        print("JSON received (in speak): ", message_json)

    if "utterance" in message_json.keys():
        # publish speaking status to general
        publish_json = {"speaking": True}
        publish_string = json.dumps(publish_json)
        mqtt_client.publish("mydaemon/general", publish_string)

        # print the JSON
        print("JSON published: ", publish_json)

        # speak the utterance
        myd_tts_speak(message_json["utterance"])
        print("Speaking: ", message_json["utterance"])

        # publish speaking status to general
        publish_json = {"speaking": False}
        publish_string = json.dumps(publish_json)
        mqtt_client.publish("mydaemon/general", publish_string)

        # print the JSON
        print("JSON published: ", publish_json)

    # if "shutdown" in message_json.keys():
    #    print("Shutdown received")
    #    call("sudo shutdown -h now", shell=True)


def main(broker_address):
    mqtt_client = mqtt.Client()  # create new instance
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(broker_address, 1883)  # connect to broker

    mqtt_client.loop_forever()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='mqtt broker address')
    parser.add_argument('--broker', dest='broker_address', type=str, help='IP of MQTT broker')

    args = parser.parse_args()
    print("The broker address is: ", args.broker_address)
    main(args.broker_address)



