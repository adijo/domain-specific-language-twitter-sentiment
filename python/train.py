#!/usr/bin/env python

"""
Trains the models for tweet classification.
"""

__author__ = "Aditya Joshi"
__version__ = "1.0"
__email__ = "1adityajoshi@gmail.com"

import numpy as np 

from sklearn.naive_bayes import BernoulliNB
from sklearn.feature_extraction.text import CountVectorizer
import re
from nltk.corpus import stopwords
import pickle
import sys
from sklearn import linear_model, datasets
import cPickle
from cleaner import clean

VECTORIZER = CountVectorizer(min_df = 1)
DELIMITER = ","


def train():
    f = open(sys.argv[1], "r")
    corpus = []
    target = []
    failed = 0
    for line in f:
        try:
            pieces = line.split(DELIMITER)
            pieces = map(lambda x : x[1:len(x) - 1], pieces)
            corpus.append(clean(pieces[5]))
            target.append(int(pieces[0]))
        except:
            failed += 1
    X = VECTORIZER.fit_transform(corpus)

    # save vectorizer.
    with open('vectorizer.pkl', 'wb') as fid:
        cPickle.dump(VECTORIZER, fid)

    # save logistic regression model.
    logreg = linear_model.LogisticRegression(C=1e5)
    logreg.fit(X, np.array(target))
    with open('logreg.pkl', 'wb') as fid:
        cPickle.dump(logreg, fid)   


train()
