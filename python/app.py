from flask import Flask
from flask import Flask, jsonify
from flask import Flask, render_template, redirect, \
    url_for, request, session, flash, make_response
app = Flask(__name__)
import tweepy
from tweepy import OAuthHandler
import json
import cPickle
from cleaner import clean

CONSUMER_KEY = ""
CONSUMER_SECRET = ""
ACCESS_TOKEN = ""
ACCESS_SECRET = ""

with open("vectorizer.pkl", 'rb') as fid:
    VECTORIZER = cPickle.load(fid)

with open('logreg.pkl', 'rb') as fid:
    LOGREG = cPickle.load(fid)

auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

def number_followers(user):
    return api.get_user(user).followers_count

def get_tweets(user, limit):
    tweets = [tweet.text for tweet in api.user_timeline(screen_name = user, count = limit, include_rts = True)]
    return tweets


def avg(arr):
    return sum(arr) / float(len(arr))

def aggregation_function(arr, name):
    if name == "min":
        return min(arr)
    elif name == "max":
        return max(arr)
    elif name == "avg":
        return avg(arr)
    else:
        return 0

@app.route("/predict", methods = ["GET"])
def predict():
    if request.method == "GET":
        person = request.args.get("person")
        followers_count = int(request.args.get("followers"))
        number_tweets = int(request.args.get("tweets"))
        tweet_class = request.args.get("class")
        aggregation_name = request.args.get("aggregation")
        followers = number_followers(person)
        if followers > followers_count:
            # calculate
            tweets = get_tweets(person, number_tweets)
            # clean the tweets.
            tweets_cleaned = map(clean, tweets)
            transformed = VECTORIZER.transform(tweets_cleaned)
            predictions = map(lambda x : LOGREG.predict_proba(x), transformed)
            predictions = map(lambda x : (x[0][0], x[0][1]), predictions)
            predictions = map(lambda x : {"pos" : x[1], "neg" : x[0]}, predictions)
            aggregation = None
            if tweet_class == "pos":
                # for positive tweets.
                reqd = map(lambda x : x["pos"], predictions)
                aggregation = "For the last %d tweets, the %s of all %s tweets is %f" % (number_tweets, aggregation_name, tweet_class, 
                                                                            aggregation_function(reqd, aggregation_name))
            else:
                # aggregation for negative tweets.
                reqd = map(lambda x : x["neg"], predictions)
                aggregation = "For the last %d tweets, the %s of all %s tweets is %f" % (number_tweets, aggregation_name, tweet_class,
                                                                             aggregation_function(reqd, aggregation_name))

            return json.dumps({"empty" : False, "predictions" : zip(tweets, predictions), "result" : aggregation})
        else:
            return json.dumps({"empty" : True, "predictions" : [], "result" : aggregation})

if __name__ == "__main__":
    app.run()