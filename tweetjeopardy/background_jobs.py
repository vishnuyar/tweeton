"""Retrieve tweets, embedding, save into database"""

import basilica
import tweepy
from decouple import config
from flask_sqlalchemy import SQLAlchemy
from .models import DB,Tweet, User

TWITTER_AUTH = tweepy.OAuthHandler(config('TWITTER_CONSUMER_KEY'),
                                   config('TWITTER_CONSUMER_SECRET'))
TWITTER_AUTH.set_access_token(config('TWITTER_ACCESS_TOKEN'),
                              config('TWITTER_ACCESS_TOKEN_SECRET'))
TWITTER = tweepy.API(TWITTER_AUTH)

BASILICA = basilica.Connection(config('BASILICA_KEY'))
TWEETS_QTY = 200
#to do - add functions later


def get_old_tweets_background():
    """Update all the existing users with their old tweets"""
    users = User.query.all()
    for user in users:
        username = user.name
        try:
            twitter_user=TWITTER.get_user(username)
            db_user = User.query.filter(User.name == username).one()
            tweets = twitter_user.timeline(count=TWEETS_QTY,include_rts=False,
                        tweet_mode='extended', max_id=db_user.oldest_tweet_id)

            if len(tweets)>1:
                #Removing the top tweet as it already exists
                tweets = tweets[1:]
                db_user.followers = twitter_user.followers_count
                db_user.following = twitter_user.friends_count
                #adding count to the existing tweets available
                db_user.available_tweets = db_user.available_tweets+len(tweets)
                db_user.oldest_tweet_id = tweets[-1].id
                db_user.oldest_tweet = tweets[-1].created_at
                DB.session.add(db_user)
                for tweet in tweets:
                    #Calculate embedding on the full tweet
                    embedding = BASILICA.embed_sentence(tweet.full_text, model='twitter')
                    db_tweet = Tweet(id=tweet.id, text=tweet.full_text[:300],embedding=embedding)
                    db_user.tweets.append(db_tweet)
                    DB.session.add(db_tweet)
        except Exception as e:
            print('Error processing {}: {}'.format(db_user.name,e))
            raise e
        else:
            DB.session.commit()
        print(f' Old tweets updated for {username}')


def get_new_tweets_background():
    """ Update the database with user's new tweets """
    users = User.query.all()
    for user in users:
        username = user.name
        try:
            twitter_user=TWITTER.get_user(username)
            db_user = User.query.filter(User.name == username).one()
            tweets = twitter_user.timeline(count=TWEETS_QTY,include_rts=False,
                        tweet_mode='extended', since_id=db_user.newest_tweet_id)

            if len(tweets)>0:
                db_user.followers = twitter_user.followers_count
                db_user.following = twitter_user.friends_count
                #adding count to the existing tweets available
                db_user.available_tweets = db_user.available_tweets+len(tweets)
                db_user.newest_tweet_id = tweets[0].id
                db_user.last_tweeted = tweets[0].created_at
                DB.session.add(db_user)
                for tweet in tweets:
                    #Calculate embedding on the full tweet
                    embedding = BASILICA.embed_sentence(tweet.full_text, model='twitter')
                    db_tweet = Tweet(id=tweet.id, text=tweet.full_text[:300],embedding=embedding)
                    db_user.tweets.append(db_tweet)
                    DB.session.add(db_tweet)
        except Exception as e:
            print('Error processing {}: {}'.format(db_user.name,e))
            raise e
        else:
            DB.session.commit()
        print(f' Old tweets updated for {username}')

    