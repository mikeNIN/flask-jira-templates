#!/usr/bin/python

from flask import render_template, g, redirect, url_for
from flask.ext.login import current_user

from my_app import app
from my_app import profile


@app.before_request
def before_request():
    if current_user.is_authenticated:
        g.user = current_user  # return username in get_id()
    else:
        g.user = None  # or 'some fake value', whatever


@app.route('/')
def index():
    if g.user is not None:
        return redirect(url_for('profile.templates_list'))
    else:
        return redirect(url_for('auth.login'))
