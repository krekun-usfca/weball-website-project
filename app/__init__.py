from flask import Flask
from config import Config
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_googlemaps import GoogleMaps

# Initialization
# Create an application instance (an object of class Flask)
# which handles all requests.
application = Flask(__name__)
application.config.from_object(Config)
application._static_folder = 'static'
db = SQLAlchemy(application)
db.create_all()
db.session.commit()

# login_manager needs to be initiated before running the app
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(application) 
login_manager.login_message = None

# initialize Google maps
GoogleMaps(application)

bootstrap = Bootstrap(application)

# Added at the bottom to avoid circular dependencies. (Altough
# it violates PEP8 standards)
from app import classes
from app import routes