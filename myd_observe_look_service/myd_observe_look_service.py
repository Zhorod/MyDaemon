import argparse
import locale
import logging
import requests
import paho.mqtt.client as mqtt
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

    if "shutdown" in message_json.keys():
        print("Shutdown")
        sys.ext(0)


def process_video_stream(mqtt_client):
    while True:
        # Read frame from camera
        # ret, image_np = video_stream_reader.read()
        image_np = video_stream_reader.read()

        # process the image
        objects = object_detector.process_image(image_np)

        if len(objects) > 0:
            print("detected: ", objects)
            message_string = json.dumps(objects)

            message_json = {"objects": objects, "time": ""}
            message_string = json.dumps(message_json)

            # publish the JSON
            mqtt_client.publish("mydaemon/look", message_string)
            # print the JSON
            print("JSON published: ", message_string)


def main(broker_address):
    mqtt_client = mqtt.Client()  # create new instance
    mqtt_client.message_callback_add("mydaemon/general", on_message)

    #mqtt_client.on_message = on_message
    mqtt_client.connect(broker_address, 1883)  # connect to broker
    mqtt_client.subscribe("mydaemon/#", 0)

    mqtt_client.loop_start()
    process_video_stream(mqtt_client)
    mqtt_client.loop_stop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='mqtt broker address')
    parser.add_argument('--broker', dest='broker_address', type=str, help='IP of MQTT broker')

    args = parser.parse_args()
    print("The broker address is: ", args.broker_address)
    main(args.broker_address)
