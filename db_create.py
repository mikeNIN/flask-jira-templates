#!/usr/bin/python

from app import db
from app.auth.models import Users

#create db
db.create_all()
db.session.commit()

#insert

#commit
# db.session.commit()
