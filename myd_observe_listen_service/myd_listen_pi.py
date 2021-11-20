import argparse
import locale
import logging
import requests
import paho.mqtt.client as mqtt
import json
import time
import sys
import paho.mqtt.client as mqtt

from google.cloud.speech import enums
from google.cloud.speech import types
from aiy.board import Board, Led

from subprocess import call

from myd_stt_pi import myd_stt_capture

speaking = False
capturing = False
clash = False
board = Board()


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
    global board
    global clash

    message_text = msg.payload.decode('utf-8')
    try:
        message_json = json.loads(message_text)
    except Exception as e:
        print("Couldn't parse raw data: %s" % message_text, e)
    else:
        print("JSON received : ", message_json)

    if message_json["speaking"] != None:
        speaking = message_json["speaking"]
        if speaking == True:
            board.led.state = Led.OFF
            if capturing == True:
                clash = True
        else:
            board.led.state = Led.ON

    if message_json["shutdown"] != None:
        print("Shutdown received")
        call("sudo shutdown -h now", shell=True)


def listen(mqtt_client):
    global speaking
    global capturing
    global clash
    global board

    board.led.state = Led.ON

    while True:
        capturing = True
        board.led.state = Led.ON
        utterance = myd_stt_capture()
        capturing = False
        board.led.state = Led.OFF
        if clash == True:
            # we received a speaking message during capture and we cant capture when speaking
            # set clash to off
            # dont publish utterance
            clash = False
        elif utterance != None:
            # The utternace has data in it
            # Add the utterance to the JSON
            if speaking != True:
                # check again that speaking has not been set while we were capturing an utterance
                message_json = {"utterance": utterance, "time": ""}
                message_string = json.dumps(message_json)

                # publish the JSON
                mqtt_client.publish("mydaemon/listen", message_string)

                # print the JSON
                print("JSON published: ", message_json)

def main(broker_address):
    mqtt_client = mqtt.Client()  # create new instance
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(broker_address, 1883)  # connect to broker

    mqtt_client.loop_start()
    listen(mqtt_client)
    client.loop_stop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='mqtt broker address')
    parser.add_argument('--broker', dest='broker_address', type=str, help='IP of MQTT broker')

    args = parser.parse_args()
    print("The broker address is: ", args.broker_address)
    main(args.broker_address)



