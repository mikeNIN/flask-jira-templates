#!/usr/bin/python

import uuid

from my_app import db, app
from sqlalchemy.dialects.postgresql  import UUID


class Users(db.Model):
    """User class implementation, properties and methods
        according to flask-login documentation"""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), index=True, unique=True)
    passwd = db.Column(db.String(30), index=True, unique=False)
    town = db.Column(db.String(30), index=True, unique=False)
    role = db.Column(db.String(30), index=True, unique=False, default='USER')
    templates = db.relationship('TicketTemplate', backref='owner', lazy='dynamic')

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def is_script_enabled(self):
        return self.town == app.config['SCRIPT_ENABLED']

    def is_admin(self):
        return self.role == 'ADMIN'

    def __repr__(self):
        return '<User {}>'.format(self.username)


class TicketTemplate(db.Model):
    """ticket template implementation"""
    id = db.Column(db.Integer, primary_key=True)
    guid = db.Column(UUID(as_uuid=True), default=uuid.uuid1())
    project = db.Column(db.String(100), index=True, unique=False)
    issuetype = db.Column(db.String(100), index=True, unique=False)
    title = db.Column(db.String(100), index=True, unique=False)
    description = db.Column(db.String(100), index=True, unique=False)
    json_form = db.Column(db.Text, index=False, unique=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
