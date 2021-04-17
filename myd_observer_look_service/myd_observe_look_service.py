import argparse
import locale
import logging
import requests
import paho.mqtt.publish as mqtt_publish
import paho.mqtt.client as mqtt_client
import json
import time
import sys

from myd_video_stream_reader import VideoStreamReader
from myd_object_detector import ObjectDetector

video_stream_reader = VideoStreamReader('http://192.168.1.215:8000/stream.mjpg')
object_detector = ObjectDetector()

def on_connect(mqtt_client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() - if we lose the connection and
    # reconnect then subscriptions will be renewed.
    mqtt_client.subscribe("mydaemon/general")

# The callback for when a PUBLISH message is received from the server.
def on_message(mqtt_client, userdata, msg):
    # check to see if the message has valid JSON content
    # check to see if the message has valid JSON content

    message_text = msg.payload.decode('utf-8')
    try:
        message_json = json.loads(message_text)
    except Exception as e:
        print("Couldn't parse raw data: %s" % message_text, e)
    else:
        print("JSON received : ", message_json)

def process_video_stream():
    while True:
        # Read frame from camera
        # ret, image_np = video_stream_reader.read()
        image_np = video_stream_reader.read()

        # process the image
        object_detector.process_image(image_np)

def main():
    # Create an MQTT client and attach our routines to it.
    local_mqtt_client = mqtt_client.Client()
    local_mqtt_client.on_connect = on_connect
    local_mqtt_client.on_message = on_message
    local_mqtt_client.connect("test.mosquitto.org", 1883, 60)
    local_mqtt_client.loop_start()

    process_video_stream()

    local_mqtt_client.loop_stop()


if __name__ == '__main__':
    main()