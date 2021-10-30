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
        
def listen():
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
                #check again that speaking has not been set while we were capturing an utterance
                message_json = {"utterance": utterance, "time": ""}
                message_string = json.dumps(message_json)
                
                # publish the JSON
                mqtt_publish.single("mydaemon/listen", message_string, hostname="test.mosquitto.org")
                
                # print the JSON
                print("JSON published: ", message_json)
                
                # wait for a bit
                #time.sleep(1)


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


