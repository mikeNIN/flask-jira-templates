from flask import Flask, render_template
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_bootstrap import Bootstrap

from utils.ad_connector import ADConn
from utils.jira_connector import JIRAConn

# Define the WSGI application object
app = Flask(__name__)

# bcrypt instance
bcrypt = Bcrypt(app)

# Configurations
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Define the database object which is imported
db = SQLAlchemy(app)

# Define login manager
lm = LoginManager()
lm.init_app(app)

# define bootstrap
Bootstrap(app)

# Define ldap connection
ldap_ac = ADConn(app)

# Define jira connection
jira_conn = JIRAConn(app)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


# Import a module / component using its blueprint handler variable
from my_app.auth.controllers import auth as auth_module
from my_app.profile.controllers import profile as profile_module
from my_app.admin.controllers import admin as admin_module

# Register blueprint(s)
app.register_blueprint(auth_module)
app.register_blueprint(profile_module)
app.register_blueprint(admin_module)

from my_app import views
from my_app.auth import models

