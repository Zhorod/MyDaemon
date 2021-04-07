# This programme checks to see if there is an utterance on the utterance server
# If there is it uses nltk to decompse and tag the utterance
# Note that I am dealing with an utterance but considering it to be a sentence
# Paul Zanelli
# Creation date: 4th April 2020

import nltk
import requests
import time
import sys
import getopt
import pickle

import paho.mqtt.publish as mqtt_publish
import paho.mqtt.client as mqtt_client
import json

# from md_db_lookup import md_db_get_response
#from md_opengraph import md_og_get_latest_post
from md_profile_manager import MyDaemonProfileManager
from md_db_lookup import MyDaemonDBLookup
from md_eliza_A import Eliza

from md_nlp import MyDaemonNLP

class MyDaemonCorrespondenceManager:
    def __init__(self):
        print("Initialising the correspondence manager class")
        self.db_lookup = MyDaemonDBLookup()
        self.profile = MyDaemonProfileManager()
        self.eliza = Eliza()

        self.response_triple = []

        # if there is data load it
        self.load_data()

        # establish an nlp utility
        self.nlp = MyDaemonNLP()

        # cache the first name
        self.first_name = self.profile.get_first_name()

    def send_move(self, command, distance):
        qa_json = {"command": command, "distance": distance}
        qa_string = json.dumps(qa_json)
        mqtt_publish.single("mydaemon/move", qa_string, hostname="test.mosquitto.org")
        print("JSON published: ", qa_string)

    def get_db_lookup_repsonse(self, utterance, probability):
        return(self.db_lookup.get_response(utterance,probability))

    def process_user_input(self, utterance):
        # we have new input from the user
        turn_amount = 0.3
        move_amount = 1

        if utterance.lower() == "shutdown" or utterance.lower() == "shut down":
            sys.exit()
        elif utterance.lower() == "forward":
            self.send_move("forward", move_amount)
            return("forward")
        elif utterance.lower() == "back":
            self.send_move("back", move_amount)
            return ("back")
        elif utterance.lower() == "left":
            self.send_move("left", turn_amount)
            return ("left")
        elif utterance.lower() == "right":
            self.send_move("right", turn_amount)
            return ("right")
        elif utterance.lower() == "print graph":
            self.profile.md_graph.print_graph()
            return ("I have printed the graph.")
        elif utterance.lower() == "print graph":
            relation = ""
            self.profile.md_graph.print_graph_relation(relation)
            return ("I have printed the graph showing, " + relation + ", relationships")
        elif utterance.lower() == "update data":
            self.profile.update_data_FB()
            return ("I have updated the facebook data")
        elif utterance.lower() == "save profile":
            self.dump_data()
            return ("I have saved the profile.")

        # get a response for the database lookup
        # will only return a result if it is above probability

        probability = 0.8
        response = self.db_lookup.get_response(utterance, probability)

        if response != "":
            # We have a response from the DB so should use it
            return (response)

        # try to get an unprocessed entity
        next_unprocessed_entity = self.profile.get_next_unprocessed_entity()

        #if next_unprocessed_entity != "":
        #    print("Unread entity is:", next_unprocessed_entity)
        #    # build latest post response and return
        #    response = self.first_name + ". Can you tell me more about " + next_unprocessed_entity
        #    return (response)

        # try to get an unprocessed post
        #next_unread_post = self.profile.get_next_unprocessed_post()
        #if next_unread_post != "":
        #    print("Unread post is:", next_unread_post)
        #    # build latest post response and return
        #    response = self.first_name + ". Can you tell me more about your recent Facebook post that said: " + next_unread_post
        #    return (response)

        # default to chatbot
        response = self.eliza.get_next_response(utterance)

        return (response)

    def load_data(self):
        try:
            with open('profile.txt', 'rb') as filehandle:
                self.profile = pickle.load(filehandle)
        except:
            print("No file to load data from")

    def dump_data(self):
        try:
            with open('profile.txt', 'wb') as filehandle:
                pickle.dump(self.profile, filehandle)
        except:
            print("Failed to open file")


MyDaemonCorrespondenceManager_ = MyDaemonCorrespondenceManager()

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() - if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("mydaemon/user")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):

    # Check that the message is in the right format
    message_text = msg.payload.decode('utf-8')
    try:
        message_json = json.loads(message_text)
    except Exception as e:
        print("Couldn't parse raw data: %s" % message_text, e)
    else:
        print("JSON received : ", message_json)

        if message_json["user"] != "":

            response = MyDaemonCorrespondenceManager_.process_user_input(message_json["user"])

            # post the response
            response_json = {"user": message_json["user"], "mydaemon": response}
            response_string = json.dumps(response_json)
            mqtt_publish.single("mydaemon/mydaemon", response_string, hostname="test.mosquitto.org")
            print("JSON published: ", response_string)
        else:
            # Publish an empty message to keep the conversation going
            # This will force anybody listening to the "mydaemon" topic to run their callback
            # this should ensure that MyDaemon is listening
            message_json["mydaemon"] = ""
            message_text = json.dumps(message_json)
            mqtt_publish.single("mydaemon/mydaemon", message_text, hostname="test.mosquitto.org")
            print("JSON published: ", message_json)

def main(argv):

        local_mqtt_client = mqtt_client.Client()
        local_mqtt_client.on_connect = on_connect
        local_mqtt_client.on_message = on_message
        local_mqtt_client.connect("test.mosquitto.org", 1883, 60)

        # We are alive - say something

        utterance = "Yo!"
        statement_response_json = {"user": "", "mydaemon": utterance}
        statement_response_string = json.dumps(statement_response_json)
        mqtt_publish.single("mydaemon/mydaemon", statement_response_string, hostname="test.mosquitto.org")
        print("JSON published: ", statement_response_string)

        while True:
                local_mqtt_client.loop_forever()

if __name__ == '__main__':
    main(sys.argv[1:])