# This is the interface to the FB open graph
# We will use a class to buffer data from the oFB open graph
# Start with name and updates, then images
# Paul Zanelli
# 20th May 2020

import json
import facebook

import imaplib
import email
from email.header import decode_header
from collections import Counter


from md_graph_manager import MyDaemonGraph
from md_nlp import MyDaemonNLP

class MyDaemonProfileManager:
    def __init__(self):
        # initialising the profile manager class
        print("initialising the profile manager class")

        # local graph class
        self.md_graph = MyDaemonGraph()

        # local nlp class
        self.md_nlp = MyDaemonNLP()

        self.first_name = ""
        self.middle_name = ""
        self.last_name = ""
        self.home_location = ""
        self.current_location = ""
        self.birthday = ""
        self.profile = ""

        self.processed_posts = set()
        self.new_posts = set()

        self.processed_likes = set()
        self.new_likes = set()

        self.num_entities = 0
        self.entity_list = []
        self.processed_entities = {}
        self.new_entities = {}

        self.num_noun_phrases = 0
        self.noun_phrases_list = []

        self.processed_noun_phrases = set()
        self.new_noun_phrases = set()

        self.new_emails = set()
        self.processed_emails = set()

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
            next_entity = self.new_entities.pop()
        except:
            return("")
        self.processed_entities.add(next_entity)
        return(next_entity)

    def extract_noun_phrases(self, text):
        print("Extracting noun phrases")
        # get the new noun phrases
        noun_phrases = self.md_nlp.processNounPhrases(text)
        for noun_phrase in noun_phrases:
            self.num_noun_phrases += 1
            #self.noun_phrases_list.append(list(noun_phrase.items())[0][0])
            self.noun_phrases_list.append(noun_phrase)

            if noun_phrase not in self.processed_noun_phrases:
                if noun_phrase not in self.new_noun_phrases:
                    # we have a new noun phrase
                    self.new_noun_phrases.add(noun_phrase)
                    print("New noun phrase: ", noun_phrase)

    def extract_entitites(self, text):
        entities = self.md_nlp.processEntities(text)
        for entity in entities:
            self.num_entities += 1
            self.entity_list.append(list(entity.items())[0][0])
            for key in entity.keys():
                if key not in list(self.processed_entities.keys()):
                    if key not in list(self.new_entities.keys()):
                        # we have a new people entity
                        self.new_entities.update(entity)
                        print("New entity: ", entity)

    def update_FB(self):

        # short lived access token - watch loading to Git
        access_token = ""
        try:
            graph = facebook.GraphAPI(access_token)
        except:
            print("failed to access FP OpenGraph API")
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
                    #noun_phrases = self.md_nlp.processNounPhrases(message)
                    #for noun_phrase in noun_phrases:
                    #    if noun_phrase not in self.processed_noun_phrases:
                    #        if noun_phrase not in self.new_noun_phrases:
                    #            # we have a new noun phrase
                    #            self.new_noun_phrases.add(noun_phrase)
                    #            print("New noun phrase: ", noun_phrase)

                    # get the entities
                    self.extract_entitites()

                    # get the noun phrases
                    self.extract_noun_phrases()

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

                        # get the entities
                        self.extract_entitites()

                        # get the noun phrases
                        self.extract_noun_phrases()

    def update_email(self):
        email_user = "p.zanelli@btopenworld.com"
        # input('Email: ')
        email_pass = ""
        # input('Password: ')

        # log in and access emails in Inbox
        # Can get list of all folders and iterate

        imap = imaplib.IMAP4_SSL('mail.btinternet.com', 993)
        imap.login(email_user, email_pass)
        status, number_messages = imap.select("Inbox")

        if status == "OK":
            number_messages = int(number_messages[0])
            print("The number of messages is: ", number_messages)

            # number of emails to process
            download_number = 100

            for i in range(number_messages, number_messages - download_number, -1):
                # fetch the email message by ID
                #print("Fetching message: ",i)
                res, msg = imap.fetch(str(i), "(RFC822)")
                md_email = {"subject": "", "sender": "", "body": ""}

                for response in msg:
                    if isinstance(response, tuple):
                        # parse a bytes email into a message object
                        msg = email.message_from_bytes(response[1])
                        # decode the email subject
                        try:
                            md_email["subject"] = decode_header(msg["Subject"])[0][0]
                        except:
                            md_email["subject"] = ""
                        if isinstance(md_email["subject"], bytes):
                            # if it's a bytes, decode to str
                            md_email["subject"] = md_email["subject"].decode()
                        # email sender
                        md_email["sender"] = msg.get("From")
                        # if the email message is multipart
                        if msg.is_multipart():
                            # iterate over email parts
                            for part in msg.walk():
                                # extract content type of email
                                content_type = part.get_content_type()
                                content_disposition = str(part.get("Content-Disposition"))
                                try:
                                    # get the email body
                                    body = part.get_payload(decode=True).decode()
                                except:
                                    pass
                                if content_type == "text/plain" and "attachment" not in content_disposition:
                                    md_email["body"] = body
                                #elif content_type == "text/html":
                                #    print("Ignoring HTML content")
                                #else:
                                #    print("Ignoring unknown content")
                        else:
                            # extract content type of email
                            content_type = msg.get_content_type()
                            content_disposition = str(msg.get("Content-Disposition"))
                            try:
                                # get the email body
                                body = msg.get_payload(decode=True).decode()
                            except:
                                pass
                            if content_type == "text/plain" and "attachment" not in content_disposition:
                                md_email["body"] = body
                            #elif content_type == "text/html":
                            #    print("Ignoring HTML content")
                            #else:
                            #    print("Ignoring unknown content")
                                # if it's HTML, create a new HTML file and open it in browser
                            #    if not os.path.isdir(subject):
                            #        # make a folder for this email (named after the subject)
                            #        os.mkdir(subject)
                            #    filename = f"{subject[:50]}.html"
                            #    filepath = os.path.join(subject, filename)
                            #    # write the file
                            #    open(filepath, "w").write(body)
                            #    # open in the default browser
                            #    webbrowser.open(filepath)

                # should have a subject, sender and message
                if md_email["body"] != "" and md_email["subject"] != "" and md_email["sender"] != "":

                    # all elements exist
                    # remove tabs and newlines
                    # need a more elegant way of cleaning the text

                    md_email["body"] = md_email["body"].replace('\n',"")
                    md_email["body"] = md_email["body"].replace('\t',"")
                    md_email["subject"] = md_email["subject"].replace('\n',"")
                    md_email["subject"] = md_email["subject"].replace('\t',"")
                    md_email["sender"] = md_email["sender"].replace('\n',"")
                    md_email["sender"] = md_email["sender"].replace('\t',"")
                    text_md_email = json.dumps(md_email)

                    if text_md_email not in self.processed_emails:
                        if text_md_email not in self.new_emails:
                            # this is a new email
                            #print("New email: ", md_email)
                            self.new_emails.add(text_md_email)

                            # get the entities
                            self.extract_entitites(md_email["body"])
                            self.extract_entitites(md_email["subject"])

                            # get the noun phrases
                            self.extract_noun_phrases(md_email["body"])
                            self.extract_noun_phrases(md_email["subject"])

                            # process the text
                            #self.md_graph.process_text(md_email["body"])
                            #self.md_graph.process_text(md_email["subject"])
                #else:
                #    print("Part of the email was missing")
        else:
            print("Failed to access emails")
        print("The total numnber of entities is: ", self.num_entities)
        print("The total numnber of noun phrases is: ", self.num_noun_phrases)

        entity_freq = []
        for w in self.entity_list:
            entity_freq.append(self.entity_list.count(w))

        noun_phrases_freq = []
        for w in self.noun_phrases_list:
            noun_phrases_freq.append(self.noun_phrases_list.count(w))

        #print("String\n" + wordstring + "\n")
        #print("List\n" + str(self.entity_list) + "\n")
        #print("Frequencies\n" + str(wordfreq) + "\n")
        #print("Pairs\n" + str(list(zip(self.entity_list, wordfreq))))

        c = Counter(self.entity_list)
        most_occur = c.most_common(100)
        for occur in most_occur:
            entity_label = self.new_entities[occur[0]]
            print("Entity: ", occur[0], " , ", occur[1], " , ", entity_label)
        #print("The higest occurances", most_occur)

        c = Counter(self.noun_phrases_list)
        most_occur = c.most_common(100)
        for occur in most_occur:
            print("Noun phrase: ", occur[0], " , ", occur[1], " , ")

        imap.close()
        imap.logout()

    def add_text_to_graph(self, text):
        self.md_graph.process_text(text)

    def add_triple_to_graph(self, triple):
            print("profile manager adding triple to graph: ", triple)
            #self.md_graph.add_triple(triple)
            self.md_graph.add_triple(triple)

    def print_graph(self):
        self.md_graph.print_graph()