"""Main application for twitoff"""

#imports
from decouple import config
from flask import Flask, render_template, request
from .models import DB, User
from .twitter import add_user_tweets,update_all_users,get_previous_tweets
from .predict import predict_user

def create_app():
    """create and configures an instance of a flask app"""
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = config('DATABASE_URL')
    app.config['ENV'] = config('FLASK_ENV') #should change this later to production
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False

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
            if request.method == 'POST':
                add_user_tweets(name)
                message = "User {} successfully added!".format(name)
                users = User.query.all()
        except Exception as e:
            message = "Error adding {}: {}".format(name,e)
        return render_template('base.html', message=message, users=users)

    #Shows the 5 recent tweets of the user selected
    @app.route('/user/<name>', methods=['GET'])
    def showuser_tweets(name):
        try:
            if request.method == 'GET':
                tweets = User.query.filter(User.name == name).one().tweets
                message = f'Latest tweets of {name}'
        except Exception as e:
            message = "Error adding {}: {}".format(name,e)
            tweets=[]
        return render_template('user.html', title=name, tweets=tweets[:5],
        message=message)

    #On submitting the selected users and tweet message predicts the user who would have said it.
    @app.route('/compare', methods=['POST'])
    def compare():
        selected_users = request.form.getlist("selectusers")
        print(selected_users)
        if (len(selected_users) >0):
            tweet_text = request.values['tweet_tweet']
            prediction = predict_user(selected_users,tweet_text)
            jeopardymessage = '"{}" is more likely to be said by {}'.format(
                    tweet_text, selected_users[int(prediction)])
        else:
            jeopardymessage = "Please select atleast two users to play"
        users = User.query.all()
        return render_template('base.html', jeopardymessage=jeopardymessage,users=users)

    #Function to update the existings users with their latest tweets
    @app.route('/updateall')
    def update():
        update_all_users()
        users = User.query.all()
        return render_template('base.html', title='Home', users=users)

    #Will get all the old tweets of the user selected
    @app.route('/previous/<username>')
    def get_previous_tweets(username):
        print(username)
        get_previous_tweets(username)
        users = User.query.all()
        return render_template('base.html', title='Home', users=users)

    return app