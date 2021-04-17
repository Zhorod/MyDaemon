# This file is the main element of the OODA service
# OODA stands for observe, orient, decide, act

import paho.mqtt.publish as mqtt_publish
import paho.mqtt.client as mqtt_client
import json
import time
import sys

class MyDaemonDecide:
    def __init__(self):
        print("Initialising the decide service class")
        self.unprocessed_utterances = []
        self.unprocessed_objects = []
        self.turn_amount = 0.3
        self.move_amount = 1

    def send_move(self, command, distance):
        qa_json = {"command": command, "distance": distance}
        qa_string = json.dumps(qa_json)
        mqtt_publish.single("mydaemon/move", qa_string, hostname="test.mosquitto.org")
        print("JSON published: ", qa_string)

    def get_db_lookup_repsonse(self, utterance, probability):
        return(self.db_lookup.get_response(utterance,probability))

    def speak_objects(self):
        for i in range(len(self.unprocessed_objects)):
            print("speaking objects")

    def check_commands(self):
        for i in range(len(self.unprocessed_utterances)):
            if self.unprocessed_utterances[i]["utterance"].lower() == "shutdown":
                self.unprocessed_utterances.pop(i)
                sys.exit()
            elif self.unprocessed_utterances[i]["utterance"].lower() == "shut down":
                self.unprocessed_utterances.remove("shut down")
                sys.exit()
            elif self.unprocessed_utterances[i]["utterance"].lower() == "forward":
                self.unprocessed_utterances.pop(i)
                self.send_move("forward", self.move_amount)
                break
            elif self.unprocessed_utterances[i]["utterance"].lower() == "back":
                self.unprocessed_utterances.pop(i)
                self.send_move("back", self.move_amount)
                break
            elif self.unprocessed_utterances[i]["utterance"].lower() == "left":
                self.unprocessed_utterances.pop(i)
                self.send_move("left", self.turn_amount)
                break
            elif self.unprocessed_utterances[i]["utterance"].lower() == "right":
                self.unprocessed_utterances.pop(i)
                self.send_move("right", self.turn_amount)
                break
            elif self.unprocessed_utterances[i]["utterance"].lower() == "what can you see":
                self.unprocessed_utterances.pop(i)
                self.speak_objects()
                break

    def process(self):
        # first think we do is respond to any direct commands
        self.check_commands()

MyDaemonDecide_ = MyDaemonDecide()

#def on_connect(client, userdata, flags, rc):
#    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() - if we lose the connection and
    # reconnect then subscriptions will be renewed.
#    client.subscribe("mydaemon/user")

# specific callback function for message that have the topic "mydaemon/
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
            #MyDaemonDecide_.unprocessed_utterances.append({"utterance": message_json["utterance"], "time": message_json["time"]})
            print("added new objects " + message_json["objects"] + " at time " + message_json["time"])
        else:
            print("the look message had a missing key")

def on_message(client, userdata, msg):
    print("received message in on_message callback: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

def decide():
    while True:
        #print("Deciding")
        #response_json = {"utterance": "left", "time": "now"}
        #response_string = json.dumps(response_json)
        #mqtt_publish.single("mydaemon/speak", response_string, hostname="test.mosquitto.org")
        #print("JSON published: ", response_string)

        MyDaemonDecide_.process()

        time.sleep(0.2)

def main(argv):

    local_mqtt_client = mqtt_client.Client()
    local_mqtt_client.message_callback_add("mydaemon/listen", on_listen_message)
    local_mqtt_client.message_callback_add("mydaemon/look", on_look_message)
    #local_mqtt_client.on_connect = on_connect
    local_mqtt_client.on_message = on_message
    local_mqtt_client.connect("test.mosquitto.org", 1883, 60)
    local_mqtt_client.subscribe("mydaemon/#", 0)
    local_mqtt_client.loop_start()

    decide()

    local_mqtt_client.loop_stop()

if __name__ == '__main__':
    main(sys.argv[1:])

#if utterance.lower() == "shutdown" or utterance.lower() == "shut down":
#    sys.exit()
#elif utterance.lower() == "forward":
#    self.send_move("forward", move_amount)
#    return ("forward")
#elif utterance.lower() == "back":
#    self.send_move("back", move_amount)
#    return ("back")
#elif utterance.lower() == "left":
#    self.send_move("left", turn_amount)
#    return ("left")
#elif utterance.lower() == "right":
#    self.send_move("right", turn_amount)
#    return ("right")
#elif utterance.lower() == "print graph":
#    self.profile.md_graph.print_graph()
#    return ("I have printed the graph.")
#elif utterance.lower() == "print graph":
#    relation = ""
#    self.profile.md_graph.print_graph_relation(relation)
#    return ("I have printed the graph showing, " + relation + ", relationships")
#elif utterance.lower() == "update data":
#    self.profile.update_data_FB()
#    return ("I have updated the facebook data")
#elif utterance.lower() == "save profile":
#    self.dump_data()
#    return ("I have saved the profile.")
# get a response for the database lookup
# will only return a result if it is above probability
#probability = 0.8
#response = self.db_lookup.get_response(utterance, probability)
#if response != "":
# We have a response from the DB so should use it
#    return (response)
# try to get an unprocessed entity
#next_unprocessed_entity = self.profile.get_next_unprocessed_entity()
# default to chatbot
#response = self.eliza.get_next_response(utterance)