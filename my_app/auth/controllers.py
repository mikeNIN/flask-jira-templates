#!/usr/bin/python

from flask import (
    Blueprint, render_template, flash, g,
    redirect, url_for, request, session
)
from flask.ext.login import current_user, login_required, login_user, logout_user

from my_app import lm, db, ldap_ac, app
from my_app.auth.forms import LoginForm
from .models import Users

# Define the blueprint: 'auth'
auth = Blueprint('auth', __name__, template_folder='templates', static_folder='static')


# Set the route and accepted methods
@auth.before_request
def before_request():
    if current_user.is_authenticated:
        g.user = current_user  # return username in get_id()
    else:
        g.user = None  # or 'some fake value', whatever


# Given *user_id*, return the associated User object.
@lm.user_loader
def load_user(id):
    return Users.query.get(int(id))


# Set the route and accepted methods
@auth.route('/login', methods=['GET', 'POST'])
def login():
    # If sign in form is submitted
    if current_user.is_authenticated:
        flash('You are already logged in.')
        return redirect(url_for('profile.templates_list'))

    form = LoginForm(request.form)

    if request.method == 'POST' and form.validate_on_submit():
        user = request.form.get('login_name')
        username = app.config['LDAP_DOMAIN'] + user
        password = request.form.get('password_field')
        try:
            auth_object = ldap_ac.authenticate(username, password, 'l', app.config['LDAP_BASE_DN'],
                                               app.config['LDAP_FILTER'])
            user_db = Users.query.filter_by(username=user).first()
            if not user_db:
                user_db = Users(username=user, town=auth_object[1]['l'][0].lower(), role='USER')
            user_db.authenticated = True
            db.session.add(user_db)
            db.session.commit()
            login_user(user_db)
            return redirect(url_for('index'))
        except:
            flash(
                'Invalid username or password. Please try again.',
                'danger')
            return render_template('login.html', form=form)
    if form.errors:
        flash(form.errors, 'error')
    return render_template('login.html', form=form)


@auth.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))     

