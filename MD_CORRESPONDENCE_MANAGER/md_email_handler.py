import imaplib
import email
import pickle
import spacy
import sys
from spacy.lang.en import English
from email.header import decode_header
from text_preprocessor import normalise_text
from collections import Counter

class MyDaemonEmailHandler:
    def __init__(self):
        # initialising the profile manager class
        print("initialising the email handler class")

        self.emails = []
        self.entitites = dict()
        self.noun_chunks = []

    def load_emails(self):
        print("Loading emails")
        try:
            with open('emails.txt', 'rb') as filehandle:
                self.emails = pickle.load(filehandle)
                self.entitites = pickle.load(filehandle)
                self.noun_chunks = pickle.load(filehandle)
        except:
            print("No file to load data from")

    def save_emails(self):
        print("saving emails")
        try:
            with open('emails.txt', 'wb') as filehandle:
                pickle.dump(self.emails, filehandle)
                pickle.dump(self.entitites, filehandle)
                pickle.dump(self.noun_chunks, filehandle)
        except:
            print("Failed to open file")

    def get_emails(self):
        input('Email: ')
        input('Password: ')
        # email_user = ""
        # email_pass = ""

        mail_server = "mail.btinternet.com"
        mail_port = 993

        # number of emails to process
        download_number = 1

        # log in and access emails in Inbox
        # Can get list of all folders and iterate

        imap = imaplib.IMAP4_SSL(mail_server, mail_port)
        imap.login(email_user, email_pass)
        status, number_messages = imap.select("Inbox")

        if status == "OK":
            number_messages = int(number_messages[0])
            print("The number of messages is: ", number_messages)
            for i in range(number_messages, number_messages - download_number, -1):
                # fetch the email message by ID
                # print("Fetching message: ",i)
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
                                # elif content_type == "text/html":
                                #    print("Ignoring HTML content")
                                # else:
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
                            # elif content_type == "text/html":
                            #    print("Ignoring HTML content")
                            # else:
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
                    #md_email["body"] = md_email["body"].replace('\n', "")
                    #md_email["body"] = md_email["body"].replace('\t', "")
                    #md_email["subject"] = md_email["subject"].replace('\n', "")
                    #md_email["subject"] = md_email["subject"].replace('\t', "")
                    #md_email["sender"] = md_email["sender"].replace('\n', "")
                    #md_email["sender"] = md_email["sender"].replace('\t', "")
                    #text_md_email = json.dumps(md_email)

                    if md_email not in self.emails:
                        # this is a new email
                        print("New email: ", md_email)
                        self.emails.append(md_email)
                # else:
                #    print("Part of the email was missing")
        else:
            print("Failed to access emails")
        imap.close()
        imap.logout()

def extract_relations(doc):
    spans = list(doc.ents) + list(doc.noun_chunks)
    for span in spans:
        span.merge()

    triples = []

    for ent in doc.ents:
        preps = [prep for prep in ent.root.head.children if prep.dep_ == "prep"]
        for prep in preps:
            for child in prep.children:
                triples.append((ent.text, "{} {}".format(ent.root.head, prep), child.text))

    return triples

def main():
    TEXT = 'Marie Curie was born on November 1867, 7. She ' \
           'was a Polish and naturalised-French physicist and chemist who conducted pioneering research on radioactivity...'

    md_email = MyDaemonEmailHandler()
    #md_email.get_emails()
    #md_email.save_emails()
    md_email.load_emails()

    # load the spacy model
    #nlp = spacy.load('en_core_web_sm')
    nlp = spacy.load('en_core_web_lg')

    number_relations = 0

    # process each email subject, sender, body
    for email in md_email.emails:
        for key, value in email.items():
            #print("The raw text is: ", value)
            normalised_text = normalise_text(value,html_stripping=True, contraction_expansion=True,
                     accented_char_removal=True, text_lower_case=False,
                     text_lemmatization=False, special_char_removal=False,
                     stopword_removal=False, remove_digits=False)
            #print("The normalised text is: ", normalised_text)
            doc = nlp(normalised_text)  # subject, sender, body
            relations = extract_relations(doc)
            for r1, r2, r3 in relations:
                number_relations += 1
                print('({}, {}, {})'.format(r1, r2, r3))
            #sys.exit()

    print("The number of relations is: ", number_relations)

if __name__ == '__main__':
    main()