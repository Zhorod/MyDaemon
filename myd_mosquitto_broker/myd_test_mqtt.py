import paho.mqtt.client as mqtt
import argparse
import time
import sys
import json

def on_connect(mqtt_client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # Subscribing in on_connect() - if we lose the connection and
    # reconnect then subscriptions will be renewed.
    mqtt_client.subscribe("mydaemon")

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
        
def main(broker_address):
    
    client = mqtt.Client() #create new instance
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker_address, 1883) #connect to broker
    
    client.loop_start()
    while True:
        message_json = {"utterance": "this is the message", "time": ""}
        message_string = json.dumps(message_json)
        client.publish("mydaemon",message_string)
        time.sleep(1)
        
    client.loop_stop()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='mqtt broker address')
    parser.add_argument('--broker', dest='broker_address', type=str, help='IP of MQTT broker')
    
    args = parser.parse_args()
    print("The broker address is: ",args.broker_address)
    main(args.broker_address)


