# This programme checks to see if there is an utterance on the utterance server
# If there is it uses nltk to decompse and tag the utterance
# Note that I am dealing with an utterance but considering it to be a sentence
# Paul Zanelli
# Creation date: 4th April 2020

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

        self.question = ""
        self.response_triple = []
        self.question_entity = ""
        self.exchange = False
        self.exchange_type = ""

        # if there is data load it
        self.load_data()

        # establish an nlp utility
        self.nlp = MyDaemonNLP()

        # cache the first name
        self.first_name = self.profile.get_first_name()

    def process_user_response_PEOPLE(self, user_text, question_text):
        print("processing response to a question")
        triple = self.nlp.processTextTripleSingle(user_text)
        if triple != "" and triple[1] != "" and triple[2] != "":
            self.response_triple= triple
            response = self.question_entity + ". " + self.response_triple[1] + ". " + self.response_triple[2]

            #response = self.response_triple[0] + ". " + self.response_triple [1] + ". " + self.response_triple [2]
            self.exchange_type = "CONFIRM"
        else:
            # failed to complete exchange - reset
            response = "Hmmmmmmm!"
            self.exchange_type = ""
            self.exchange = False
            self.question = ""
        return(response)

    def process_user_response_CONFIRM(self, user_text, question_text):
        # check to see if it is a yes or a no or not sure
        print("checking for answer")
        if user_text.lower() == "yes":
            # we have a confirmed triple
            # add the triple the graph in the profile
            self.profile.add_triple_to_graph(self.response_triple)
            response = "Got it!"
        else:
            response = "Hmmmmmmmmm!"
        self.exchange_type = ""
        self.question_entity = ""
        self.exchange = False
        self.question = ""
        return (response)

    def get_db_lookup_repsonse(self, utterance, probability):
        return(self.db_lookup.get_response(utterance,probability))

    def process_user_input(self, utterance):
        # we have new input from the user

        # is this the start of an exchange
        if utterance.lower() == "shutdown" or utterance.lower() == "shut down":
            sys.exit()
        if utterance.lower() == "print graph":
            self.exchange_type = ""
            self.question_entity = ""
            self.exchange = False
            self.question = ""
            self.profile.md_graph.print_graph()
            return ("I have printed the graph.")
        if utterance.lower() == "print graph":
            self.exchange_type = ""
            self.question_entity = ""
            self.exchange = False
            self.question = ""
            relation = ""
            self.profile.md_graph.print_graph_relation(relation)
            return ("I have printed the graph showing, " + relation + ", relationships")
        if utterance.lower() == "update facebook":
            self.exchange_type = ""
            self.question_entity = ""
            self.exchange = False
            self.question = ""
            self.profile.update_FB()
            return ("I have updated the facebook data")
        if utterance.lower() == "update email":
            self.exchange_type = ""
            self.question_entity = ""
            self.exchange = False
            self.question = ""
            self.profile.update_email()
            return ("I have updated the email")
        if utterance.lower() == "save profile":
            self.exchange_type = ""
            self.question_entity = ""
            self.exchange = False
            self.question = ""
            self.dump_data()
            return ("I have saved the profile.")

        if self.exchange:
            # we are already in an exchange
            # call the response based on the exchange type
            if self.exchange_type == "PEOPLE":
                response = self.process_user_response_PEOPLE(utterance, self.question)
                return (response)
            if self.exchange_type == "CONFIRM":
                response = self.process_user_response_CONFIRM(utterance, self.question)
                return (response)

        # get a response for the database lookup
        # will only return a result if it is above probability

        probability = 0.8
        response = self.db_lookup.get_response(utterance, probability)

        if response != "":
            # We have a response from the DB so should use it
            return (response)

        # try to get an unprocessed entity
        next_unprocessed_entity = self.profile.get_next_unprocessed_entity()
        if next_unprocessed_entity != "":
            print("Unread entity is:", next_unprocessed_entity)
            # build latest post response and return
            response = self.first_name + ". Can you tell me more about " + next_unprocessed_entity
            self.question = response
            self.question_entity = next_unprocessed_entity
            self.exchange = True
            self.exchange_type = "PEOPLE"
            return (response)

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
                filehandle.close()
        except:
            print("No file to load data from")

    def dump_data(self):
        try:
            with open('profile.txt', 'wb') as filehandle:
                pickle.dump(self.profile, filehandle)
                filehandle.close()
        except:
            print("Failed to open file")


MyDaemonCorrespondenceManager_ = MyDaemonCorrespondenceManager()

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() - if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("user")

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

    # Check that the topic is "user" which indicates a message from the user
    if msg.topic == "user":
            # The msg has content from user
            if message_json["user"] != "":

                response = MyDaemonCorrespondenceManager_.process_user_input(message_json["user"])

                # post the response
                qa_json = {"user": message_json["user"], "mydaemon": response}
                qa_string = json.dumps(qa_json)
                mqtt_publish.single("mydaemon", qa_string, hostname="test.mosquitto.org")
                print("JSON published: ", qa_string)
            else:
                # Publish an empty message to keep the conversation going
                # This will force anybody listening to the "mydaemon" topic to run their callback
                # this should ensure that MyDaemon is listening
                message_json["mydaemon"] = ""
                message_text = json.dumps(message_json)
                mqtt_publish.single("mydaemon", message_text, hostname="test.mosquitto.org")
                print("JSON published: ", message_json)

def text_test():
    #while True:

        #print("Waiting for input: ")
        #user_input = input()
        user_input = "update email"
        response = MyDaemonCorrespondenceManager_.process_user_input(user_input)
        print(response)


def main(argv):

        local_mqtt_client = mqtt_client.Client()
        local_mqtt_client.on_connect = on_connect
        local_mqtt_client.on_message = on_message
        local_mqtt_client.connect("test.mosquitto.org", 1883, 60)

        # We have jsut started up so we need to start the conversation
        # At this point we have assumed that this is the first time MyDaemon has been switched on
        # The first question is therefore "what is your name"

        text_test()

        #question = "Hello, how are you"
        #qa_json = {"user": "", "mydaemon": question}
        #qa_string = json.dumps(qa_json)
        #mqtt_publish.single("mydaemon", qa_string, hostname="test.mosquitto.org")
        #print("JSON published: ", qa_string)

        #while True:
        #        local_mqtt_client.loop_forever()

if __name__ == '__main__':
    main(sys.argv[1:])