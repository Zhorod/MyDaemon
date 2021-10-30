# This file is the main element of the OODA service
# OODA stands for observe, orient, decide, act

import paho.mqtt.publish as mqtt_publish
import paho.mqtt.client as mqtt_client
import json

class MyDaemonOODAService:
    def __init__(self):
        print("Initialising the OODA service class")
        # what are we seeing and hearing - observe
        # need to know where we are - orient
        # need to decide what we are going to do
        # need to act

        self.decision = "nothing"

    def observe(self):
        print("Observe")

    def orient(self):
        print("Orient")

    def decide(self):
        print("Decide")

    def act(self):
        print("Act")

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

        # default to chatbot
        response = self.eliza.get_next_response(utterance)

        return (response)

MyDaemonOODAService_ = MyDaemonOODAService()

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