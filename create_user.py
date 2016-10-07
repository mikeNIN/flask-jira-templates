#!/usr/bin/python

import sys

from flask import current_app
from getpass import getpass

from my_app import bcrypt, db, app
from my_app.auth.models import Users


def main():
    """Creating users in database. Used only in development env"""
    with app.app_context():
        db.metadata.create_all(db.engine)
        if Users.query.all():
            create = raw_input("A user already exists! Create another? (y/n): ")
            if create in ['n', 'no', 'No', 'NO']:
                return
        print "Enter user name: ",
        username = raw_input()
        print "Enter town: ",
        town = raw_input()
        role = raw_input("What role (press Enter for user or enter ADMIN): ")   
        password = getpass()
        assert password == getpass('Password (again):')
        if role == '':
            user = Users(username=username, passwd=bcrypt.generate_password_hash(password), town=town)
        else:
            user = Users(username=username, passwd=bcrypt.generate_password_hash(password), town=town, role=role)
        db.session.add(user)
        db.session.commit()
        print 'User added.'

if __name__ == '__main__':
    if main():
        print "Successfully added new user"
