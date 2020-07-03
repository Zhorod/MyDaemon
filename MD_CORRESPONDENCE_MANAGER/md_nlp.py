# Paul Zanelli
# 22nd May 2020
# nlp functions

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
#from md_gm_db import md_gm_db_get_response

class MyDaemonNLP:
    def __init__(self):
        # self.nlp = spacy.load('en_core_web_lg')  # can use the large model though takes a while to load
        self.nlp = spacy.load('en_core_web_sm')

    def getSentences(self, text):
        nlp = English()
        nlp.add_pipe(nlp.create_pipe('sentencizer'))
        document = nlp(text)
        return [sent.string.strip() for sent in document.sents]

    def printToken(self, token):
        print(token.text, "->", token.dep_)

    def appendChunk(self , original, chunk):
        return (original + ' ' + chunk)

    def isRelationCandidate(self, token):
        deps = ["ROOT", "adj", "attr", "agent", "amod"]
        return any(subs in token.dep_ for subs in deps)

    def isConstructionCandidate(self, token):
        deps = ["compound", "prep", "conj", "mod"]
        return any(subs in token.dep_ for subs in deps)

    def processSubjectObjectPairs(self, tokens):
        subject = ''
        object = ''
        relation = ''
        subjectConstruction = ''
        objectConstruction = ''
        # print("The tokens are: ", tokens)
        for token in tokens:
            # self.printToken(token)
            if "punct" in token.dep_:
                continue
            if self.isRelationCandidate(token):
                relation = self.appendChunk(relation, token.lemma_)
            if self.isConstructionCandidate(token):
                if subjectConstruction:
                    subjectConstruction = self.appendChunk(subjectConstruction, token.text)
                if objectConstruction:
                    objectConstruction = self.appendChunk(objectConstruction, token.text)
            if "subj" in token.dep_:
                subject = self.appendChunk(subject, token.text)
                subject = self.appendChunk(subjectConstruction, subject)
                subjectConstruction = ''
            if "obj" in token.dep_:
                object = self.appendChunk(object, token.text)
                object = self.appendChunk(objectConstruction, object)
                objectConstruction = ''

        #print (subject.strip(), ",", relation.strip(), ",", object.strip())
        return (subject.strip().lower(), relation.strip().lower(), object.strip().lower())

    def processNounPhrases(self, text):
        sentences = self.getSentences(text)
        noun_phrases = []
        # print("The sentences are: ", sentences)

        for sent in sentences:
            # print("The sentence is: ", sent)
            doc = self.nlp(sent)

            doc = self.nlp(sent)
            for chunk in doc.noun_chunks:
                noun_phrases.append(chunk.text)
                #print("Appending to noun phrases: ", chunk.text)
        return (noun_phrases)

    def processEntities(self, text):
        entities = []
        sentences = self.getSentences(text)
        # print("The sentences are: ", sentences)

        for sent in sentences:
            doc = self.nlp(sent)
            for entity in doc.ents:
                entities.append({entity.text: entity.label_})
        return (entities)

    def printGraph(self, triples):
        # triple: subject, relation, object

        G = nx.Graph()
        for triple in triples:
            G.add_node(triple[0])
            G.add_node(triple[1])
            G.add_node(triple[2])
            G.add_edge(triple[0], triple[1])
            G.add_edge(triple[1], triple[2])

        pos = nx.spring_layout(G)
        plt.figure()
        nx.draw(G, pos, edge_color='black', width=1, linewidths=1,
                node_size=500, node_color='seagreen', alpha=0.9,
                labels={node: node for node in G.nodes()})
        plt.axis('off')
        plt.show()

    def printGraphRelation(self, triples, relation):

        # extract subjects

        source = [i[0] for i in triples]

        # extract object
        relations = [i[1] for i in triples]

        # extract relations
        target = [i[2] for i in triples]

        print("The relations are: ", relations)

        kg_df = pd.DataFrame({'source': source, 'target': target, 'edge': relations})

        G = nx.from_pandas_edgelist(kg_df[kg_df['edge'] == relation], "source", "target",
                                    edge_attr=True, create_using=nx.MultiDiGraph())
        plt.figure(figsize=(10, 10))
        pos = nx.spring_layout(G, k=0.5)  # k regulates the distance between nodes
        nx.draw(G, with_labels=True, node_color='skyblue', node_size=1500, edge_cmap=plt.cm.Blues, pos=pos)
        plt.show()

        #plt.figure(figsize=(12, 12))

        #pos = nx.spring_layout(G, k=0.5)  # k regulates the distance between nodes
        #nx.draw(G, with_labels=True, node_color='skyblue', node_size=1500, edge_cmap=plt.cm.Blues, pos=pos)
        #plt.show()


        #G = nx.Graph()
        #for triple in triples:
        #    G.add_node(triple[0])
        #    G.add_node(triple[1])
        #    G.add_node(triple[2])
        #    G.add_edge(triple[0], triple[1])
        #    G.add_edge(triple[1], triple[2])

        #pos = nx.spring_layout(G)
        #plt.figure()
        #nx.draw(G, pos, edge_color='black', width=1, linewidths=1,
        #        node_size=500, node_color='seagreen', alpha=0.9,
        #        labels={node: node for node in G.nodes()})
        #plt.axis('off')
        #plt.show()

    def getEntities(self, text):
        ## chunk 1
        ent1 = ""
        ent2 = ""

        prv_tok_dep = ""  # dependency tag of previous token in the sentence
        prv_tok_text = ""  # previous token in the sentence

        prefix = ""
        modifier = ""

        for tok in self.nlp(text):
            # self.printToken(tok)
            ## chunk 2
            # if token is a punctuation mark then move on to the next token
            if tok.dep_ != "punct":
                # check: token is a compound word or not
                if tok.dep_ == "compound":
                    prefix = tok.text
                    # if the previous word was also a 'compound' then add the current word to it
                    if prv_tok_dep == "compound":
                        prefix = prv_tok_text + " " + tok.text

                # check: token is a modifier or not
                if tok.dep_.endswith("mod") == True:
                    modifier = tok.text
                    # if the previous word was also a 'compound' then add the current word to it
                    if prv_tok_dep == "compound":
                        modifier = prv_tok_text + " " + tok.text

                ## chunk 3
                if tok.dep_.find("subj") == True:
                    ent1 = modifier + " " + prefix + " " + tok.text
                    prefix = ""
                    modifier = ""
                    prv_tok_dep = ""
                    prv_tok_text = ""

                ## chunk 4

                if tok.dep_.find("obj") == True or tok.dep_ == "attr":
                    ent2 = modifier + " " + prefix + " " + tok.text

                ## chunk 5
                # update variables
                prv_tok_dep = tok.dep_
                prv_tok_text = tok.text

        return [ent1.strip(), ent2.strip()]

    def getRelation(self, text):
        doc = self.nlp(text)

        # Matcher class object
        matcher = Matcher(self.nlp.vocab)

        # define the pattern
        pattern = [{'DEP': 'ROOT'},
                   {'DEP': 'prep', 'OP': "?"},
                   {'DEP': 'agent', 'OP': "?"},
                   {'POS': 'ADJ', 'OP': "?"}]

        matcher.add("matching_1", None, pattern)

        matches = matcher(doc)
        k = len(matches) - 1

        span = doc[matches[k][1]:matches[k][2]]

        return (span.text)

    def processTextTriples(self, text):
        sentences = self.getSentences(text)
        triples = []

        for sentence in sentences:
            print("The sentence is: ", sentence)
            if sentence != "":
                doc = self.nlp(sentence)
                triple = self.processSubjectObjectPairs(doc)
                lower_triple = [triple[0].lower(), triple[1].lower(), triple[2].lower()]

                print("THe candidate triple is: ", triple)
                if lower_triple[0] != "" and lower_triple[1] != "" and lower_triple[2] != "":
                    triples.append(lower_triple)
                    print("Found triple: ", lower_triple)
        return (triples)

    def processTextTriplesNew(self, text):
        # triple: subject, relation, object

        sentences = self.getSentences(text)
        triples = []

        for sentence in sentences:
            print("The sentence is: ", sentence)
            if sentence != "":
                entity_pair = self.getEntities(sentence)
                relation = self.getRelation(sentence)
                triple = [entity_pair[0].lower(), relation.lower(), entity_pair[1].lower()]
                if triple[0] != "" and triple[1] != "" and triple[2] != "":
                    triples.append(triple)
                    print("Found triple: ", triple)
        return(triples)

    def processTextTripleSingle(self, text):
        entity_pair = self.getEntities(text)
        relation = self.getRelation(text)
        triple = [entity_pair[0], relation, entity_pair[1]]
        if triple[0] != "" and triple[1] != "" and triple[2] != "":
            print("Found triple: ", triple)
        else:
            print("No triple found")
            triple[0] = ""
            triple[1] = ""
            triple[2] = ""

        return(triple)