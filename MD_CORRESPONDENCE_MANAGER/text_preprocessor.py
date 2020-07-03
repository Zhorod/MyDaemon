import spacy
import pandas as pd
import numpy as np
import nltk
from nltk.tokenize.toktok import ToktokTokenizer
import re
from bs4 import BeautifulSoup
from contractions import CONTRACTION_MAP
import unicodedata

#nlp = spacy.load('en_core', parse=True, tag=True, entity=True)
#nlp = spacy.load('en_core_web_lg')
nlp = spacy.load('en_core_web_sm')
#nlp_vec = spacy.load('en_vecs', parse = True, tag=True, #entity=True)
tokenizer = ToktokTokenizer()
stopword_list = nltk.corpus.stopwords.words('english')
stopword_list.remove('no')
stopword_list.remove('not')


def strip_html_tags(text):
    soup = BeautifulSoup(text, "html.parser")
    stripped_text = soup.get_text()
    return stripped_text

def remove_accented_chars(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8', 'ignore')
    return text


def expand_contractions(text, contraction_mapping=CONTRACTION_MAP):
    contractions_pattern = re.compile('({})'.format('|'.join(contraction_mapping.keys())),
                                      flags=re.IGNORECASE | re.DOTALL)

    def expand_match(contraction):
        match = contraction.group(0)
        first_char = match[0]
        expanded_contraction = contraction_mapping.get(match) \
            if contraction_mapping.get(match) \
            else contraction_mapping.get(match.lower())
        expanded_contraction = first_char + expanded_contraction[1:]
        return expanded_contraction

    expanded_text = contractions_pattern.sub(expand_match, text)
    expanded_text = re.sub("'", "", expanded_text)
    return expanded_text

def remove_special_characters(text, remove_digits=False):
    pattern = r'[^a-zA-z,!?.-0-9\s]' if not remove_digits else r'[^a-zA-z,!?.-\s]'
    text = re.sub(pattern, '', text)
    return text

def simple_stemmer(text):
    ps = nltk.porter.PorterStemmer()
    text = ' '.join([ps.stem(word) for word in text.split()])
    return text

def lemmatize_text(text):
    text = nlp(text)
    text = ' '.join([word.lemma_ if word.lemma_ != '-PRON-' else word.text for word in text])
    return text

def remove_stopwords(text, is_lower_case=False):
    tokens = tokenizer.tokenize(text)
    tokens = [token.strip() for token in tokens]
    if is_lower_case:
        filtered_tokens = [token for token in tokens if token not in stopword_list]
    else:
        filtered_tokens = [token for token in tokens if token.lower() not in stopword_list]
    filtered_text = ' '.join(filtered_tokens)
    return filtered_text


def normalise_text(raw_text, html_stripping=True, contraction_expansion=True,
                     accented_char_removal=True, text_lower_case=True,
                     text_lemmatization=True, special_char_removal=True,
                     stopword_removal=True, remove_digits=True):
    normalised_text = raw_text
    # strip HTML
    if html_stripping:
        normalised_text = strip_html_tags(normalised_text)
    # remove accented characters
    if accented_char_removal:
        normalised_text = remove_accented_chars(normalised_text)
    # expand contractions
    if contraction_expansion:
        normalised_text = expand_contractions(normalised_text)
    # lowercase the text
    if text_lower_case:
        normalised_text = normalised_text.lower()
    # remove extra newlines
    doc = re.sub(r'[\r|\n|\r\n]+', ' ', normalised_text)
    # lemmatize text
    if text_lemmatization:
        doc = lemmatize_text(normalised_text)
    # remove special characters and\or digits
    if special_char_removal:
        # insert spaces between special characters to isolate them
        special_char_pattern = re.compile(r'([{.(-)!}])')
        normalised_text = special_char_pattern.sub(" \\1 ", normalised_text)
        normalised_text = remove_special_characters(normalised_text, remove_digits=remove_digits)
        # remove extra whitespace
    normalised_text = re.sub(' +', ' ', normalised_text)
    # remove stopwords
    if stopword_removal:
        normalised_text = remove_stopwords(normalised_text, is_lower_case=text_lower_case)

    return normalised_text

def main():
    raw_text = ["So long and thanks for all the fish.","Paul Zanelli is a super Python coder."]
    normalised_text = normalise_text(raw_text)
    print(raw_text)
    print(normalised_text)

if __name__ == '__main__':
    main()