# This is the interface to the FB open graph
# We will use a class to buffer data from the oFB open graph
# Start with name and updates, then images
# Paul Zanelli
# 20th May 2020

import sys
import json
import facebook
import pickle

from md_graph_manager import MyDaemonGraph
from md_nlp import MyDaemonNLP

class MyDaemonProfileManager:
    def __init__(self):
        # initialising the profile manager class
        print("initialising the profile manager class")

        self.first_name = ""
        self.middle_name = ""
        self.last_name = ""
        self.home_location = ""
        self.current_location = ""
        self.birthday = ""

        self.processed_posts = set()
        self.new_posts = set()

        self.processed_likes = set()
        self.new_likes = set()

        self.processed_people_entities = set()
        self.new_people_entities = set()

        self.processed_noun_phrases = set()
        self.new_noun_phrases = set()

        self.profile = ""

        # local graph class
        self.md_graph = MyDaemonGraph()

        # local nlp class
        self.md_nlp = MyDaemonNLP()

    def get_first_name(self):
        return (self.first_name)

    def get_next_unprocessed_post(self):
        # get the next new post
        try:
            next_post = self.new_posts.pop()
        except:
            return("")
        self.processed_posts.add(next_post)
        return (next_post)

    def get_next_unprocessed_entity(self):
        # get the next new entity
        try:
            next_entity = self.new_people_entities.pop()
        except:
            return("")
        self.processed_people_entities.add(next_entity)
        return(next_entity)

    def update_data_FB(self):

        # short lived access token - watch loading to Git
        access_token = ""
        try:
            graph = facebook.GraphAPI(access_token)
        except:
            print("failed to access FP OpenGrpah API")
            return(False)


        # get the first name and location
        self.profile = graph.get_object('me', fields='first_name, last_name,location')
        #print("The profile is: ", self.profile)
        self.first_name = self.profile["first_name"]
        print("The first name is: ", self.first_name)
        self.last_name = self.profile["last_name"]
        print("The last name is: ", self.last_name)
        self.location = self.profile["location"]["name"]
        print("The location is: ", self.location)

        # get the posts
        # only add the ones we have not seen
        new_posts = graph.get_connections(id='me', connection_name='posts')
        for new_post in new_posts["data"]:
            # print("New post: ", new_post)
            try:
                message = new_post["message"]
            except:
                message = ""
                continue
            if message not in self.processed_posts:
                if message not in self.new_posts:
                    # we have a new post
                    print("New post: ", message)
                    self.new_posts.add(message)
                    self.md_graph.process_text(message)

                    # for every new post
                    # get the new noun phrases
                    noun_phrases = self.md_nlp.processNounPhrases(message)
                    for noun_phrase in noun_phrases:
                        if noun_phrase not in self.processed_noun_phrases:
                            if noun_phrase not in self.new_noun_phrases:
                                # we have a new noun phrase
                                self.new_noun_phrases.add(noun_phrase)
                                print("New noun phrase: ", noun_phrase)

                    # get the entities
                    people_entities = self.md_nlp.processPeopleEntities(message)
                    for people_entity in people_entities:
                        if people_entity not in self.processed_people_entities:
                            if people_entity not in self.new_people_entities:
                                # we have a new people entity
                                self.new_people_entities.add(people_entity)
                                print("New entity: ", people_entity)
                            continue

            new_likes = graph.get_connections(id='me', connection_name='likes')
            for new_like in new_likes["data"]:
                try:
                    message = new_like["message"]
                except:
                    message = ""
                    continue
                if message not in self.processed_likes:
                    if message not in self.new_likes:
                        # we have a new like
                        print("New like: ", message)
                        self.new_likes.add(message)
                        self.md_graph.process_text(message)

                        # for every new like
                        # get the new noun phrases
                        noun_phrases = self.md_nlp.processNounPhrases(message)
                        for noun_phrase in noun_phrases:
                            if noun_phrase not in self.processed_noun_phrases:
                                if noun_phrase not in self.new_noun_phrases:
                                    # we have a new noun phrase
                                    self.new_noun_phrases.add(noun_phrase)
                                    print("New noun phrase: ", noun_phrase)

                        # get the entities
                        people_entities = self.md_nlp.processPeopleEntities(message)
                        for people_entity in people_entities:
                            if people_entity not in self.processed_people_entities:
                                if people_entity not in self.new_people_entities:
                                    # we have a new people entity
                                    self.new_people_entities.add(people_entity)
                                    print("New entity: ", people_entity)

    def add_text_to_graph(self, text):
        self.md_graph.process_text(text)

    def add_triple_to_graph(self, triple):
            print("profile manager adding triple to graph: ", triple)
            #self.md_graph.add_triple(triple)
            self.md_graph.add_triple(triple)

    def print_graph(self):
        self.md_graph.print_graph()

    #def dump_data(self):
    #    # open output file for writing
    #    with open('profile.txt', 'w') as filehandle:

    #       filehandle.write(self.first_name)
    #        filehandle.write(self.middle_name)
    #        filehandle.write(self.last_name)
    #        filehandle.write(self.home_location)
    #        filehandle.write(self.current_location)
    #        filehandle.write(self.birthday)

    #        filehandle.write(str(self.processed_posts))
    #        filehandle.write(str(self.new_posts))
    #        filehandle.write(str(self.processed_likes))
    #        filehandle.write(str(self.new_likes))
    #        filehandle.write(str(self.processed_people_entities))
    #        filehandle.write(str(self.new_people_entities))
    #        filehandle.write(str(self.processed_noun_phrases))
    #        filehandle.write(str(self.new_noun_phrases))

    #def load_data(self):
        # open output file for reading
    #    with open('profile.txt', 'r') as filehandle:
    #        self.first_name = ast.literal_eval(filehandle.read())
    #        self.middle_name = ast.literal_eval(filehandle.read())
    #        self.last_name = ast.literal_eval(filehandle.read())
    #        self.home_location = ast.literal_eval(filehandle.read())
    #        self.current_location = ast.literal_eval(filehandle.read())
    #        self.birthday = ast.literal_eval(filehandle.read())

    #        self.processed_posts = ast.literal_eval(filehandle.read())
    #        self.new_posts = ast.literal_eval(filehandle.read())
    #        self.processed_likes = ast.literal_eval(filehandle.read())
    #        self.new_likes = ast.literal_eval(filehandle.read())
    #        self.processed_people_entities = ast.literal_eval(filehandle.read())
    #        self.new_people_entities = ast.literal_eval(filehandle.read())
    #        self.processed_noun_phrases = ast.literal_eval(filehandle.read())
    #        self.new_noun_phrases = ast.literal_eval(filehandle.read())

