import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from datetime import timedelta

# Create a login manager object
login_manager = LoginManager()

app = Flask(__name__)
UPLOAD_FOLDER='upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['SECRET_KEY'] = 'mysecretkey'
basedir = os.path.abspath(os.path.dirname(__file__))
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://iqzwkgpqdohsws:73f4aed745090d609fa70717fe474d506c667f15e941df5c6b8f8605314272f1@ec2-18-210-214-86.compute-1.amazonaws.com:5432/dev57ds8h0mm5k?ssl=true'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)
db = SQLAlchemy(app)



Migrate(app,db)


# pass in our app to the login manager
#login_manager.init_app(app)

# Tell users what view to go to when they need to login.
#login_manager.login_view = "login"
