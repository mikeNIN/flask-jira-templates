#!/usr/bin/python

import json
from jira import JIRA
from my_app import app

'''
    get metadata for given project and issuetype
    save as json file
'''


def convert_keys_to_string(dictionary):
    """Recursively converts dictionary keys to strings."""
    if not isinstance(dictionary, dict):
        return dictionary
    return dict((str(k), convert_keys_to_string(v))
                for k, v in dictionary.items())


jira = JIRA(options={'server': app.config['JIRA_SERVER'], 'verify': False},
            basic_auth=(app.config['JIRA_USER'], app.config['JIRA_SECRET']),
            get_server_info=False)

for issuetype in app.config['JIRA_ISSUE_TYPES']:
    jira_meta = jira.createmeta(projectKeys=app.config['JIRA_PROJECT'], issuetypeNames=issuetype,
                                expand='projects.issuetypes.fields')
    jira_dict = jira_meta['projects'][0]
    dict_from_jra_dict = convert_keys_to_string(jira_dict)
    json.dump(dict_from_jra_dict['issuetypes'][0], file(issuetype+'.json', 'w'), indent=4)
