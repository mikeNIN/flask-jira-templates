#!/usr/bin/python

"""
    module similar to ad_connector; it's purpose is to
    create jira connection and put it on app stack
    also it has proxy function for JIRA class functions
"""

import requests

from jira import JIRA
from jira import JIRAError as jiraer
from flask import current_app, g
from flask import _app_ctx_stack as stack

from requests.packages.urllib3.exceptions import InsecureRequestWarning, InsecurePlatformWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)

__all__ = ('JIRAConn',)


class JIRAConn(object):

    jiraer.log_to_tempfile = False

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.options = {
            'server': app.config['JIRA_SERVER'],
            'rest_api_version': 'latest',
            'verify': False
        }

        app.extensions['jira_conn'] = self

        app.teardown_appcontext(self.teardown)

    def connect(self, username, password):

        try:
            jira_conn = JIRA(options=self.options, basic_auth=(username, password), validate=True,
                             get_server_info=False)
            return jira_conn
        except jiraer as e:
            print "connect excetion"
            return e
        except requests.HTTPError as e:
            print "another " + e
        except requests.ConnectionError as e:
            print "cerr " + e

    def teardown(self, exception):
        if hasattr(g, 'jira_conn'):
            g.jira_conn.kill_session()

        ctx = stack.top
        if hasattr(ctx, 'jira_conn'):
            ctx.jira_conn.kill_session()

    def connection(self):
        if hasattr(g, 'jira_conn'):
            return g.jira_conn

        ctx = stack.top
        if ctx is not None:
            if not hasattr(ctx, 'jira_conn'):
                ctx.jira_conn = self.connect(
                    current_app.config['JIRA_USER'],
                    current_app.config['JIRA_SECRET']
                )
            return ctx.jira_conn

    def create_issue(self, fields_):
        try:
            response = self.connection().create_issue(fields=fields_)
            return response
        except jiraer as e:
            return e
