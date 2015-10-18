#!/usr/bin/env python

"""
Cleaner functions.
"""

__author__ = "Aditya Joshi"
__version__ = "1.0"
__email__ = "1adityajoshi@gmail.com"


import re
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
STEMMER = PorterStemmer()
STOP_WORDS = stopwords.words("english")
STEMMER = PorterStemmer()
USER_REGEX = re.compile(r"\@[^\ ]+")
HASH_REGEX = re.compile(r"#")
URL_REGEX = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')


def stem_sentence(sentence):
    res = " ".join([STEMMER.stem(kw) for kw in sentence.split(" ")])
    return res
def word_mention(sentence):
    return USER_REGEX.sub("AT_USER", sentence)

def remove_hash(sentence):
    return USER_REGEX.sub("", sentence)

def remove_url(sentence):
    return URL_REGEX.sub("URL", sentence)

def remove_stop_words(text):
    text = ' '.join([word for word in text.split() if word not in STOP_WORDS])
    return text

def remove_non_alphabet(sentence):
    sentence = sentence.split()


def clean(sentence):
    sentence = sentence.lower()
    return stem_sentence(word_mention(remove_url(remove_hash(remove_stop_words(sentence)))))
