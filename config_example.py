import os

# Statement for enabling the development environment
DEBUG = True

# Define the application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
print BASE_DIR

# Define the database - we are working with
SQLALCHEMY_DATABASE_URI = 'path-to-our-database'
DATABASE_CONNECT_OPTIONS = {}

# define ldap3 Server options
LDAP_SERVER = 'ldap-server'
LDAP_PORT = ''
LDAP_USE_SSL = 'True'
LDAP_TIMEOUT = 10

# define ldap3 Conection options
LDAP_CONNECTION_STRATEGY = 'SYNC'
LDAP_BIND = 'AUTO_BIND_NO_TLS'
LDAP_BINDUSR = ''
LDAP_SECRET = ''

# search options
LDAP_FILTER = ''
LDAP_BASE_DN = ''
LDAP_DOMAIN = ''

# allowed labels (list)
labels_allowed = []

SCRIPT_ENABLED = ''

# define jira-python object options
JIRA_SERVER = ''
JIRA_USER = ''
JIRA_SECRET = ''

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED = True

#TODO: create better solution for keeping and generating keys
# Use a secure, unique and absolutely secret key for
# signing the data. 
CSRF_SESSION_KEY = ''

# Secret key for signing cookies
SECRET_KEY = ''
