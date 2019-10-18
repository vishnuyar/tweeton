"""Retrieve tweets, embedding, save into database"""

import basilica
import tweepy
from decouple import config
from .models import DB, Tweet, User

TWITTER_AUTH = tweepy.OAuthHandler(config('TWITTER_CONSUMER_KEY'),
                                   config('TWITTER_CONSUMER_SECRET'))
TWITTER_AUTH.set_access_token(config('TWITTER_ACCESS_TOKEN'),
                              config('TWITTER_ACCESS_TOKEN_SECRET'))
TWITTER = tweepy.API(TWITTER_AUTH)

BASILICA = basilica.Connection(config('BASILICA_KEY'))

#to do - add functions later

def add_user_tweets(username):
    """Add a new user and their Tweets, or else error"""
    try:
        twitter_user=TWITTER.get_user(username)
        db_user= User(id=twitter_user.id, name=username)
        DB.session.add(db_user)
        tweets = twitter_user.timeline(count=200,include_rts=False, tweet_mode='extended')
        if tweets:
            db_user.newest_tweet_id = tweets[0].id
            db_user.followers = twitter_user.followers_count
            db_user.following = twitter_user.friends_count
            db_user.available_tweets = len(tweets)
            db_user.oldest_tweet_id = tweets[-1].id
            db_user.oldest_tweet = tweets[-1].created_at
            db_user.last_tweeted = tweets[0].created_at
            for tweet in tweets:
                #Calculate embedding on the full tweet
                embedding = BASILICA.embed_sentence(tweet.full_text, model='twitter')
                db_tweet = Tweet(id=tweet.id, text=tweet.full_text[:300],embedding=embedding)
                db_user.tweets.append(db_tweet)
                DB.session.add(db_tweet)
        else:
            raise Exception("Player doesn't exist in Twitter world")
    except Exception as e:
        print('Error processing {}: {}'.format(username,e))
        raise e
    else:
        DB.session.commit()

def update_all_users():
    """Update all the existing users with their latest tweets"""
    try:
        users = User.query.all()
        for user in users:
            twitter_user=TWITTER.get_user(user.name)
            tweets = twitter_user.timeline(count=200, 
            include_rts=False, tweet_mode='extended', since_id=user.newest_tweet_id)
            if tweets:
                user.followers = twitter_user.followers_count
                user.following = twitter_user.friends_count
                #adding count to the existing tweets available
                user.available_tweets = user.available_tweets+len(tweets)
                user.newest_tweet_id = tweets[0].id
                user.last_tweeted = tweets[0].created_at
                DB.session.add(user)
                for tweet in tweets:
                    #Calculate embedding on the full tweet
                    embedding = BASILICA.embed_sentence(tweet.full_text, model='twitter')
                    db_tweet = Tweet(id=tweet.id, text=tweet.full_text[:300],embedding=embedding)
                    user.tweets.append(db_tweet)
                    DB.session.add(db_tweet)
    except Exception as e:
        print('Error processing {}: {}'.format(user.name,e))
        raise e
    else:
        DB.session.commit()

def get_previous_tweets(username):
    """ Update the database with user's old tweets """
    try:
        twitter_user=TWITTER.get_user(username)
        db_user = User.query.filter(User.name == username).one()
        tweets = twitter_user.timeline(count=200,include_rts=False,
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

def get_new_tweets(username):
    """ Update the database with user's new tweets """
    try:
        twitter_user=TWITTER.get_user(username)
        db_user = User.query.filter(User.name == username).one()
        tweets = twitter_user.timeline(count=200,include_rts=False,
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