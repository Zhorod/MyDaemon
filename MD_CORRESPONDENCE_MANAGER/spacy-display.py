import pandas as pd
import re
import spacy

from spacy import displacy
from spacy.lang.en import English


nlp = spacy.load('en_core_web_sm')

text = "Maria Curie was born on November 1867, 7. She was a Polish and naturalized-French physcicist and chemist who conducted pioneering research on radioactivity..."
print(text)
doc = nlp(text)
for chunk in doc.noun_chunks:
    print("Noun chunk: ", chunk.text, chunk.root.text, chunk.root.dep_,
            chunk.root.head.text)
for entity in doc.ents:
    print("Entity: ", entity.text, " : ", entity.label_)
sentence_spans = list(doc.sents)
displacy.serve(sentence_spans, style="dep")
#displacy.serve(sentence_spans, style="ent")