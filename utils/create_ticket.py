#!/usr/bin/python

#
# def from_immutable_to_dict(imm_dict):
#     temp_dict = {}
#     for item in imm_dict:
#         if item not in ('csrf_token'):
#             temp_dict.update({item: imm_dict.get(item)})
#     return temp_dict

from my_app import jira_conn


def translate_to_jira(request_copy):
    # here extracted data will be held
    ticket_data = {}

    for element in request_copy:
        if request_copy[element]:
            if element == 'labels':
                ticket_data.update({element: request_copy.getlist(element)})
                # request_copy.pop(element)
            if element in ('customfield_10503', 'customfield_12400', 'customfield_10802'):
                ticket_data.update({element: {'value': request_copy[element]}})
            if element in ('description', 'summary', 'customfield_10504', 'customfield_11606', 'customfield_11300',
                           'customfield_11624'):
                ticket_data.update({element: request_copy[element]})
            if element in ('customfield_11600', 'reporter', 'assignee'):
                ticket_data.update({element: {'name': request_copy[element]}})
            if element in ('customfield_11401', 'customfield_11625', 'customfield_10513'):
                ticket_data.update({element: [{'value': request_copy[element]}]})
            if element == 'customfield_10800':
                ticket_data.update({element: [{'name': request_copy[element]}]})
            if element == 'customfield_11603_child':
                pass
            if element == 'customfield_11603':
                ticket_data.update({element: {'value': request_copy[element],
                                              'child': {'value': request_copy.get('customfield_11603_child')}}})
    return ticket_data


def create_ticket_jira(request, **kwargs):
    request_copy = request.copy()
    request_copy.pop('csrf_token')
    # let's make proper dict from request object
    # request_dict = from_immutable_to_dict(request)

    # get standard elements from kwargs
    project = kwargs.get('project')
    issuetype = kwargs.get('issuetype')

    # let's extract elements not usable during ticket creation
    time_spent = request_copy.pop('time_spent', None)
    resolved = request_copy.pop('resolved', None)
    comment = request_copy.pop('comment', None)

    ticket = translate_to_jira(request_copy)
    standard = {'project': {'key': project}, 'issuetype': {'name': issuetype}}
    fields = dict(ticket, **standard)

    return jira_conn.create_issue(fields)
