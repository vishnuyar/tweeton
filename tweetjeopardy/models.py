"""Database models for the Application using SQLAlchemy"""

from flask_sqlalchemy import SQLAlchemy

DB = SQLAlchemy()

class User(DB.Model):
    """Twitter users that we pull and analyze"""
    id = DB.Column(DB.BigInteger, primary_key=True)
    name = DB.Column(DB.String(15), nullable=False)
    last_tweeted = DB.Column(DB.DateTime())
    followers = DB.Column(DB.BigInteger)
    following = DB.Column(DB.BigInteger)
    available_tweets = DB.Column(DB.Integer)
    oldest_tweet =  DB.Column(DB.DateTime())
    oldest_tweet_id = DB.Column(DB.BigInteger)
    newest_tweet_id = DB.Column(DB.BigInteger)
    
    def __repr__(self):
        return '<User {}>'.format(self.name)

class Tweet(DB.Model):
    """Tweets of the user who will be players"""
    id = DB.Column(DB.BigInteger, primary_key=True)
    text = DB.Column(DB.Unicode(300))
    tweet_time = DB.Column(DB.DateTime())
    embedding = DB.Column(DB.PickleType, nullable = False)
    user_id = DB.Column(DB.BigInteger, DB.ForeignKey('user.id'), nullable=False)
    user = DB.relationship('User', backref=DB.backref('tweets', lazy=True))

    def __repr__(self):
	       return '<Tweet {}>'.format(self.text)