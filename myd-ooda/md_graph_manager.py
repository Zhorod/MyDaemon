# Paul Zanelli
# 13th April 2020
# Class that seeks to extract knoweldge from a user utterance to build a graph

import pandas as pd
import re
import spacy
from spacy.lang.en import English

import paho.mqtt.publish as mqtt_publish
import paho.mqtt.client as mqtt_client
import json

from spacy.matcher import Matcher
from spacy.tokens import Span
import networkx as nx
import matplotlib.pyplot as plt

from md_nlp import MyDaemonNLP

class MyDaemonGraph:
    def __init__(self):

        # initialising the graph class
        print("Initialising the graph manager class")

        self.md_nlp = MyDaemonNLP()
        self.triples = []

    def add_triple(self, triple):
        if triple[0] != "" and triple[1] != "" and triple[2] != "":
            self.triples.append(triple)
            print("New triple: ", triple)
            return (True)
        else:
            print("Triple not complete: ", triple)
            return (False)

    def process_text(self, user_text):
        # get a triples from the text
        # triple should be subject,

        triples = self.md_nlp.processTextTriplesNew(user_text)
        for triple in triples:
            if triple[0] != "" and triple[1] != "" and triple[2] != "":
                found = False
                for existing_triple in self.triples:
                    if triple[0] == existing_triple[0] and triple[1] == existing_triple[1] and triple[2] == existing_triple[2]:
                        found = True
                if found == False:
                    # triple is new
                    self.triples.append(triple)
                    print("New triple: ", triple)
                else:
                   print("Triple exists")
            else:
                print("Triple not complete: ", triple)

    def print_graph(self):
        self.md_nlp.printGraph(self.triples)

    def print_graph_relation(self, relation):
        self.md_nlp.printGraphRelation(self.triples, relation)
