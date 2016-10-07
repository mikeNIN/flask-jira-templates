#!/usr/bin/python

"""
    this module creates ldap connection object and saves it
    on app stack;
    This module is based  on great Flask-LDAPConn module
    (https://github.com/rroemhild/flask-ldapconn); some functions
    are direct copies from that module
"""

from ldap3 import Server, Connection
from ldap3 import SUBTREE, NTLM
from ldap3 import LDAPInvalidDnError, LDAPInvalidFilterError, LDAPBindError, LDAPException

from flask import current_app, g
from flask import _app_ctx_stack as stack


__all__ = ('ADConn',)


class ADConn(object):

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.ldap_server = Server(
            host=app.config['LDAP_SERVER'],
            port=app.config['LDAP_PORT'],
            connect_timeout=app.config['LDAP_TIMEOUT']
        )

        # store ldpap_conn to app extensions
        app.extensions['ldap_conn'] = self

        # teardown appcontext
        app.teardown_appcontext(self.teardown)

    def connect(self, user, password):
        try:
            ldap_conn = Connection(
                self.ldap_server,
                auto_bind=True,
                client_strategy=current_app.config['LDAP_CONNECTION_STRATEGY'],
                user=user,
                password=password,
                authentication=NTLM,
                lazy=False
            )
        except LDAPException as e:
            return False, e.message
        return ldap_conn

    def teardown(self, exception):
        if hasattr(g, 'ldap_conn'):
            g.ldap_conn.unbind()

        ctx = stack.top
        if hasattr(ctx, 'ldap_conn'):
            ctx.ldap_conn.unbind()

    @property
    def connection(self):
        if hasattr(g, 'ldap_conn'):
            return g.ldap_conn

        ctx = stack.top
        if ctx is not None:
            if not hasattr(ctx, 'ldap_conn'):
                ctx.ldap_conn = self.connect(
                    current_app.config['LDAP_BINDUSR'],
                    current_app.config['LDAP_SECRET']
                )
            return ctx.ldap_conn

    def authenticate(self,
                     username,
                     password,
                     attributes=None,
                     base_dn=None,
                     search_filter=None,
                     search_scope=SUBTREE
                     ):
        # split user and get only login part
        user = username.split('\\')[1]
        user_filter = '(sAMAccountName={0})'.format(user)
        search_filter_local = '(&{0}{1})'.format(user_filter, search_filter)

        try:
            # search user in AD based on criteria
            self.connection.search(base_dn, search_filter_local, search_scope, attributes=[attributes])
            response = self.connection.response
            attribute = response[0]['attributes']

            # try to connect with this user's DN
            conn = self.connect(username, password)
            conn.unbind()
            return True, attribute
        except (LDAPInvalidDnError, LDAPInvalidFilterError, IndexError, LDAPBindError) as e:
            return False, e.message












