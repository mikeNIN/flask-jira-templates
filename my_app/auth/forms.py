#!/usr/bin/python

from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired


class LoginForm(Form):
    login_name = StringField('Username', [InputRequired()])
    password_field = PasswordField('Password', [InputRequired()])
