"""Main application for twitoff"""

#imports
from decouple import config
from flask import Flask, render_template, request
from .models import DB, User,Tweet
from .twitter import add_user_tweets,update_all_users,get_previous_tweets,get_new_tweets
from .predict import predict_user
from sqlalchemy import desc
from .background_jobs import get_new_tweets_background,get_old_tweets_background

def create_app():
    """create and configures an instance of a flask app"""
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = config('DATABASE_URL')
    #app.config['ENV'] = config('FLASK_ENV') #should change this later to production
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False

    #intialisig the database instance
    DB.init_app(app)

    #Home page of the app showing all the available users
    @app.route('/')
    def root():
        users = User.query.all()
        return render_template('base.html', title='Home', users=users,message="")

    #Adds a new user and first 200 tweets of the user if avaiable
    @app.route('/user', methods=['POST'])
    def adduser():
        name = request.values['twitter_handle']
        try:
            tweetuser = User.query.filter(User.name == name).one()
            if tweetuser:
                message = f'Player {name} already exists'
        except:
        
            try:
                add_user_tweets(name)
                message = "User {} successfully added!".format(name)
            except Exception as e:
                message = "Error encounter adding {}: {}".format(name,e)

        users = User.query.all()
        return render_template('base.html', message=message, users=users)

    #Shows the 5 recent tweets of the user selected
    @app.route('/user/<name>', methods=['GET'])
    def showuser_tweets(name):
        try:
            if request.method == 'GET':
                tweetuser = User.query.filter(User.name == name).one()
                tweets = Tweet.query.filter(Tweet.user==tweetuser).order_by(desc(Tweet.id)).limit(5)
                message = f'Latest tweets of {name}'
        except Exception as e:
            message = "Error adding {}: {}".format(name,e)
            tweets=[]
        return render_template('user.html', title=name, tweets=tweets[:5],
        message=message,user=tweetuser)

    #On submitting the selected users and tweet message predicts the user who would have said it.
    @app.route('/whotweetsthis', methods=['POST'])
    def compare():
        selected_users = request.form.getlist("selectusers")
        print(selected_users)
        if (len(selected_users) >1):
            tweet_text = request.values['tweet_tweet']
            prediction = predict_user(selected_users,tweet_text)
            jeopardymessage = '"{}" is more likely to tweet " {} "'.format(
                    selected_users[int(prediction)],tweet_text)
        else:
            jeopardymessage = "Please select atleast two users to play"
        users = User.query.all()
        return render_template('base.html', jeopardymessage=jeopardymessage,users=users)

    #Function to update the existings users with their latest tweets
    @app.route('/updateall')
    def updateall():
        update_all_users()
        users = User.query.all()
        return render_template('base.html', title='Home', users=users)

    #Function to update the selected users with their latest tweets
    @app.route('/newtweets/<username>')
    def newtweets(username):
        try:
            get_new_tweets(username)
            tweetuser = User.query.filter(User.name == username).one()
            tweets = Tweet.query.filter(Tweet.user==tweetuser).order_by(desc(Tweet.id)).limit(5)
            message = "New tweets checked for {}".format(username)
        except Exception as e:
            message = "Error adding new tweets of {}:{}".format(username,e)
            tweets = []
        return render_template('user.html', title=username, tweets=tweets[:5],
                                    message=message,user=tweetuser)

    #Will get more of the old tweets of the user selected
    @app.route('/oldtweets/<username>')
    def previoustweets(username):
        try:
            get_previous_tweets(username)
            tweetuser = User.query.filter(User.name == username).one()
            tweets = Tweet.query.filter(Tweet.user==tweetuser).order_by(desc(Tweet.id)).limit(5)
            message = "Old tweets checked for {}".format(username)
        except Exception as e:
            message = "Error gettting old tweets of {}:{}".format(username,e)
            tweets = []
        return render_template('user.html', title=username, tweets=tweets[:5],
                                    message=message,user=tweetuser)

    @app.route('/createdatabase')
    def createdatabase():
        try:
            DB.create_all()
        except Exception as e:
            message="creating database failed"
        users = User.query.all()
        return render_template('base.html', title='Home', users=users,message="")

    @app.route('/longbackgroundjobs')
    def updatetweetsoldnew():
        try:
            get_old_tweets_background()
            get_new_tweets_background()
            message = "background jobs completed"
        except Exception as e:
            message="creating database failed"
        users = User.query.all()
        return render_template('base.html', title='Home', users=users,message=message)

    return app