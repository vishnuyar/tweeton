"""Main application for twitoff"""

#imports
from decouple import config
from flask import Flask, render_template, request
from .models import DB, User
from .twitter import add_user_tweets,update_all_users

def create_app():
    """create and configures an instance of a flask app"""
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = config('DATABASE_URL')
    app.config['ENV'] = config('ENV') #should change this later to production
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False

    DB.init_app(app)

    @app.route('/')
    def root():
        users = User.query.all()
        return render_template('base.html', title='Home', users=users,message="")

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

    @app.route('/updateall')
    def update():
        update_all_users()
        users = User.query.all()
        return render_template('base.html', title='Home', users=users)
    return app