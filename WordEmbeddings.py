from gensim.models import Word2Vec
from gensim.models.phrases import Phrases
import string
import json
import os
import multiprocessing
from time import time

os.chdir("/Users/Nacho/Desktop/ChatBot Project/")   # Project directory

"""
Stopwords
"""
with open("stop_words.txt") as f:
    content = f.readlines()
# you may also want to remove whitespace characters like `\n` at the end of each line
stopwords = [x.strip() for x in content]

"""
Tokenize
"""

punctuation = string.punctuation + "«»“”‘’…—"


def simple_tokenizer(doc, lower=True):

    doc = " ".join(token for token in doc.split() if notURL(token) and not token.startswith("<@")
                                                                   and not token.startswith("@"))

    if lower:
        tokenized_doc = doc.translate(str.maketrans(
            '', '', punctuation)).lower().split()

    else:
        tokenized_doc = doc.translate(str.maketrans('', '', punctuation)).split()

    tokenized_doc = [
        token for token in tokenized_doc if token.lower() not in stopwords
    ]
    return tokenized_doc


"""
Auxiliary functions
"""

def notURL(word):

    # The word is not a URL direction
    if "https://" in word or "http://" in word:
        return False
    return True

"""
Open Database
"""

with open("MessagesJSON.txt") as f:
    data = json.load(f)

msgs = [simple_tokenizer(msg['content']) for msg in data['messages']]
print(msgs[0])

"""
Set up Model
"""

# Train a bigram detector.
bigrams  = Phrases(msgs, min_count=50)
bigrams = bigrams.freeze()
ngram = Phrases(bigrams[msgs], min_count=50)
ngram = ngram.freeze()

for i in range(40):
    print(ngram[msgs][i])

# Model
pharo_w2v = Word2Vec(min_count=10,
                      window=4,
                      vector_size=200,
                      sample=6e-5,
                      alpha=0.03,
                      min_alpha=0.0007,
                      negative=20,
                      workers=multiprocessing.cpu_count())

# Vocabulary
pharo_w2v.build_vocab(ngram[msgs], progress_per=10000)

"""
Training
"""

t = time()
pharo_w2v.train(ngram[msgs], total_examples=pharo_w2v.corpus_count, epochs=25, report_delay=10)
print('Time to train the model: {} mins'.format(round((time() - t) / 60, 2)))

# Save the model
if not os.path.exists('./w2v_models'):
    os.mkdir('./w2v_models')
pharo_w2v.save('./w2v_models/pharo_w2v_200d.model')


