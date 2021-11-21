# This file is the main element of the OODA service
# OODA stands for observe, orient, decide, act

import paho.mqtt.client as mqtt
import json
import time
import sys
import argparse

from myd_voice_db_lookup import MyDaemonDBLookup
from md_eliza_A import Eliza
from md_nlp import MyDaemonNLP

class MyDaemonDecide:
    def __init__(self):
        print("Initialising the decide service class")
        self.unprocessed_utterances = []
        self.unprocessed_objects = []
        self.turn_amount = 0.15
        self.move_amount = 1
        self.probability = 0.8 # probability of DB lookup
        self.db_lookup = MyDaemonDBLookup()
        self.eliza = Eliza()

    def send_move(self, command, distance, mqtt_client):
        qa_json = {"command": command, "distance": distance}
        qa_string = json.dumps(qa_json)
        mqtt_client.publish("mydaemon/move", qa_string)
        print("JSON published: ", qa_string)

    def get_db_lookup_repsonse(self, utterance, probability):
        return(self.db_lookup.get_response(utterance,probability))

    def speak_objects(self, mqtt_client):
        if len(self.unprocessed_objects) > 0:
            utterance = "I can see: "
            if len(self.unprocessed_objects[0]["objects"]) > 0:
                for i in range(len(self.unprocessed_objects[0]["objects"])):
                    utterance = utterance + " a " + self.unprocessed_objects[0]["objects"][i] + ";"
            print(utterance)
            qa_json = {"utterance": utterance, "time": ""}
            qa_string = json.dumps(qa_json)
            mqtt_client.publish("mydaemon/speak", qa_string)
            print("JSON published: ", qa_string)
            self.unprocessed_objects.pop(0)
        else:
            qa_json = {"utterance": "nothing yet", "time": ""}
            qa_string = json.dumps(qa_json)
            mqtt_client.publish("mydaemon/speak", qa_string)
            print("JSON published: ", qa_string)

    def check_commands(self, mqtt_client):
        for i in range(len(self.unprocessed_utterances)):
            if self.unprocessed_utterances[i]["utterance"].lower() == "shutdown":
                qa_json = {"shutdown": "shutdown", "time": ""}
                qa_string = json.dumps(qa_json)
                mqtt_client.publish("mydaemon/general", qa_string)
                print("JSON published: ", qa_string)
                self.unprocessed_utterances.pop(i)
                sys.exit()
            elif self.unprocessed_utterances[i]["utterance"].lower() == "shut down":
                qa_json = {"shutdown": "shutdown", "time": ""}
                qa_string = json.dumps(qa_json)
                mqtt_client.publish("mydaemon/general", qa_string)
                print("JSON published: ", qa_string)
                self.unprocessed_utterances.pop(i)
                sys.exit()
            elif self.unprocessed_utterances[i]["utterance"].lower() == "forward":
                self.unprocessed_utterances.pop(i)
                self.send_move("forward", self.move_amount, mqtt_client)
                return(True)
            elif self.unprocessed_utterances[i]["utterance"].lower() == "back":
                self.unprocessed_utterances.pop(i)
                self.send_move("back", self.move_amount, mqtt_client)
                return(True)
            elif self.unprocessed_utterances[i]["utterance"].lower() == "left":
                self.unprocessed_utterances.pop(i)
                self.send_move("left", self.turn_amount,mqtt_client)
                return (True)
            elif self.unprocessed_utterances[i]["utterance"].lower() == "right":
                self.unprocessed_utterances.pop(i)
                self.send_move("right", self.turn_amount,mqtt_client)
                return (True)
            elif self.unprocessed_utterances[i]["utterance"].lower() == "report":
                self.unprocessed_utterances.pop(i)
                self.speak_objects(mqtt_client)
                return (True)
            elif self.unprocessed_utterances[i]["utterance"].lower() == "what can you see":
                self.unprocessed_utterances.pop(i)
                self.speak_objects(mqtt_client)
                return (True)
            elif self.unprocessed_utterances[i]["utterance"].lower() == "what can you say":
                self.unprocessed_utterances.pop(i)
                self.speak_objects(mqtt_client)
                return (True)
        return(False)

    def check_database(self, mqtt_client):
        if len(self.unprocessed_utterances) > 0:
            response = self.db_lookup.get_response(self.unprocessed_utterances[0]["utterance"].lower(), self.probability)
            if response != "":
                qa_json = {"utterance": response, "time": ""}
                qa_string = json.dumps(qa_json)
                mqtt_client.publish("mydaemon/speak", qa_string)
                print("JSON published: ", qa_string)
                self.unprocessed_utterances.pop(0)
                return (True)
        return(False)

    def use_chatbot(self,mqtt_client):
        if len(self.unprocessed_utterances) > 0:
            response = self.eliza.get_next_response(self.unprocessed_utterances[0]["utterance"].lower())
            if response != "":
                qa_json = {"utterance": response, "time": ""}
                qa_string = json.dumps(qa_json)
                mqtt_client.publish("mydaemon/speak", qa_string)
                print("JSON published: ", qa_string)
                self.unprocessed_utterances.pop(0)
                return (True)
        return(False)

    def process(self, mqtt_client):
        # first think we do is respond to any direct commands
        if self.check_commands(mqtt_client):
            return(True)
        if self.check_database(mqtt_client):
            return (True)
        if self.use_chatbot(mqtt_client):
            return (True)
        return(False)

MyDaemonDecide_ = MyDaemonDecide()

#def on_connect(client, userdata, flags, rc):
#    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() - if we lose the connection and
    # reconnect then subscriptions will be renewed.
#    client.subscribe("mydaemon/user")

# specific callback function for message that have the topic "mydaemon/listen"
def on_listen_message(client, userdata, msg):
    print("received message in on_listen_message callback: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

    # Check that the message is in the right format
    message_text = msg.payload.decode('utf-8')
    try:
        message_json = json.loads(message_text)
    except Exception as e:
        print("Couldn't parse raw data: %s" % message_text, e)
    else:
        print("JSON received : ", message_json)
        if "utterance" in message_json and "time" in message_json:
            MyDaemonDecide_.unprocessed_utterances.append({"utterance":message_json["utterance"], "time":message_json["time"]})
            print("added new utterance " + message_json["utterance"] + " at time " + message_json["time"])
        else:
            print("the listen message had a missing key")

# specific callback function for message that have the topic "mydaemon/look"
def on_look_message(client, userdata, msg):
    print("received message in on_look_message callback: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

    # Check that the message is in the right format
    message_text = msg.payload.decode('utf-8')
    try:
        message_json = json.loads(message_text)
    except Exception as e:
        print("Couldn't parse raw data: %s" % message_text, e)
    else:
        print("JSON received : ", message_json)
        if "objects" in message_json and "time" in message_json:
            object_list = message_json["objects"]
            if len(object_list) > 0:
                MyDaemonDecide_.unprocessed_objects.insert(0,{"objects": object_list, "time": message_json["time"]})
                print("updated objects ", MyDaemonDecide_.unprocessed_objects[0])
        else:
            print("the look message had a missing key")

def on_message(client, userdata, msg):
    print("received message in on_message callback: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

def decide(mqtt_client):
    while True:
        MyDaemonDecide_.process(mqtt_client)
        time.sleep(0.2)

def main(broker_address):
    mqtt_client = mqtt.Client()  # create new instance
    mqtt_client.message_callback_add("mydaemon/listen", on_listen_message)
    mqtt_client.message_callback_add("mydaemon/look", on_look_message)

    mqtt_client.on_message = on_message
    mqtt_client.connect(broker_address, 1883)  # connect to broker
    mqtt_client.subscribe("mydaemon/#", 0)

    mqtt_client.loop_start()
    decide(mqtt_client)
    mqtt_client.loop_stop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='mqtt broker address')
    parser.add_argument('--broker', dest='broker_address', type=str, help='IP of MQTT broker')

    args = parser.parse_args()
    print("The broker address is: ", args.broker_address)
    main(args.broker_address)