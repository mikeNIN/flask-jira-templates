#!/usr/bin/python

from flask import render_template, g
from flask.ext.login import current_user

from my_app import app


@app.before_request
def before_request():
    if current_user.is_authenticated:
        g.user = current_user  # return username in get_id()
    else:
        g.user = None  # or 'some fake value', whatever


@app.route('/')
def index():
    return render_template('index.html')
