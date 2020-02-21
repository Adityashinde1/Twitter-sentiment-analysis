from flask import Flask, render_template, request
from textblob import TextBlob
import tweepy
from flask_sqlalchemy import SQLAlchemy
import os


consumer_key = '3SjtHrYo9fhZPUxdKofbXElG7'
consumer_secret = 'E2wsVRqQXJkgTsrkBo31nChCEegg0hU0GMuk2aKlcU25rgoma6'
access_token = '1127097032508755969-JhMKRDJMzgmh287WB2nJ8cZ1zPgHLu'
access_token_secret = 'V9audBEFFxmZuHGQvWA0nd8NZct6a9zhwLlpsdo9Nx8U7'


auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "twitter.db"))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = database_file
db = SQLAlchemy(app)


class Analysis(db.Model):
    sr_no = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(50))
    result = db.Column(db.String(50))


def percentage(part, whole):
    return float(part) / float(whole) * 100


def convert(s):
    str1 = ""
    return str1.join(s)


def get_tweets(term, number):
    tweets1 = tweepy.Cursor(api.search, q=term).items(number)

    positive = 0
    negative = 0
    neutral = 0
    polarity = 0
    tweets2 = []
    result = []

    for tweet in tweets1:
        tweet_text = tweet.text
        analysis = TextBlob(tweet_text)
        polarity += analysis.sentiment.polarity

        if analysis.sentiment.polarity == 0.00:
            neutral += 1
        elif analysis.sentiment.polarity < 0.00:
            negative += 1
        elif analysis.sentiment.polarity > 0.00:
            positive += 1
        tweets2.append(tweet_text)

    positive = percentage(positive, number)
    negative = percentage(negative, number)
    neutral = percentage(neutral, number)

    if positive > negative:
        result.append('Positive')
    elif positive < negative:
        result.append('Negative')
    elif positive == negative:
        result.append('Neutral')

    positive = round(positive, 2)
    negative = round(negative, 2)
    neutral = round(neutral, 2)

    tweets = (*tweets2, "\n")

    return positive, negative, neutral, convert(result), tweets[:-1]


@app.route("/")
def home():
    return render_template('home.html')


@app.route("/info.html")
def info():
    return render_template('info.html')


@app.route("/analyse", methods=['GET', 'POST'])
def analyse():
    if request.method == 'POST':
        keyword = request.form.get('keyword')
        number = int(request.form.get('number'))

    positive, negative, neutral, result, tweets = get_tweets(keyword, number)

    data = {'positive': positive, 'negative': negative, 'neutral': neutral,
            'result': result, 'keyword': keyword, 'number': number, 'tweets': tweets}

    entry = Analysis(term=keyword, result=result)
    db.session.add(entry)
    db.session.commit()
    return render_template('analysis.html', data=data)


if __name__ == '__main__':
    app.run(debug=True)




