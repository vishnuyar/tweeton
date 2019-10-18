"""Prediction of Users based on Tweet embeddings."""
import pickle
import numpy as np
from sklearn.linear_model import LogisticRegression
from .models import User
from .twitter import BASILICA

def predict_user(selected_users, tweet_text, cache=None):
    """
    Determine and return which user is more likely to tweet the text
    Using Logistic Regression for multiclassifcation using Twitter text using 
    twitter api and using the embeddings from Basilica api
    """
    user_set = pickle.dumps((selected_users))
    if cache and cache.exists(user_set):
        log_reg = pickle.loads(cache.get(user_set))
    else:
        embeddings = []
        labels = []
        for i,user in enumerate(selected_users):
            db_user = User.query.filter(User.name == user).one()        
            user_embeddings = np.array([tweet.embedding for tweet in db_user.tweets])
            if (len(embeddings)==0):
                embeddings = user_embeddings
                labels = np.ones(len(db_user.tweets))*i
            else:
                embeddings = np.vstack([embeddings, user_embeddings])
                #Label for each user is in the order of the training data being loaded
                labels = np.concatenate([labels,(np.ones(len(db_user.tweets))*i)])
        log_reg = LogisticRegression().fit(embeddings, labels)
        cache and cache.set(user_set, pickle.dumps(log_reg))
    tweet_embeddings = BASILICA.embed_sentence(tweet_text, model='twitter')
    return log_reg.predict(np.array(tweet_embeddings).reshape(1, -1))