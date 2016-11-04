# -*- encoding: utf-8 -*-

"""
    module extracts customfield values from html of create issue html page;
    because from JIRA REST you can only get all values of this customfield,
    not only the one that are enabled. As I have no direct access to jira
    database so I had to find other solution
"""

import requests
import httplib
import re
import json

from bs4 import BeautifulSoup
from my_app import app

httplib.HTTPConnection.debuglevel = 0

print requests.__version__

def get_from_jira(url):
    try:
        response = requests.get(
            url,
            auth=(app.config['JIRA_USER'], app.config['JIRA_SECRET']),
            headers={'Accept': 'application/json'}
        )

        response.raise_for_status()

        # get page content and save as bs4 object
        soup = BeautifulSoup(response.content, "lxml")

        # get content of html object with id customfield_11603, which is SR-Categories
        # parent categories
        source_parent = soup.find_all("select", id='\\"customfield_11603\\"')

        # extract only needed information as bs4.Tag object
        parent = source_parent[0].find_all(class_=re.compile('option-group'))

        # get content of html object with id customfield_11603:1, which is
        # SR-Categories subcategories
        source_children = soup.find_all("select", id='\\"customfield_11603:1\\"')

        # prepare empty dict
        # {parent: [children]}
        categories_sr = {}

        # loop through parents and extract all children of main category
        for element in parent:
            option_class = element.get('class', None)[0].strip('\\"')
            parent_category = element.getText()
            child = source_children[0].find_all(class_=re.compile(option_class))
            child_list = [item.getText() for item in child]
            categories_sr.update({parent_category: child_list})

        try:
            json.dump(categories_sr, file('customfield_11603.json', 'w'), indent=4, sort_keys=True)
            return True
        except ValueError as e:
            return e.message
        except Exception as e:
            return e.message
    except requests.exceptions.HTTPError as err:
        return err.message
    except requests.exceptions.ConnectionError as err:
        return err.message


get_from_jira(
         app.config['JIRA_SERVER'] + "/secure/QuickCreateIssue!default.jspa?decorator=none")
