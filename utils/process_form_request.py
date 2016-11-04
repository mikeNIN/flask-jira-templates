#!/usr/bin/python

"""
    main app module, takes requests object, processes it
    to create template json data and saved it in database
"""

import json
import uuid

from my_app import db, app
from my_app.auth.models import TicketTemplate, Users


# converts ImmutableMultiDict to dict
def from_immutable_to_dict(imm_dict):
    temp_dict = {}
    for item in imm_dict:
        if item not in ('save', 'required', 'csrf_token', 'resolved'):
            temp_dict.update({item: imm_dict.get(item)})
    return temp_dict


def process_all(request_data, user_id, issuetype, **kwargs):

    user = Users.query.filter_by(id=user_id.get_id()).first()
    path_to_json = app.config['JIRA_SOURCE_FILES'][issuetype]
    with open(path_to_json, 'r') as data_file:
        fields_file = json.load(data_file)
    default = []

    if user.role == 'ADMIN':

        required_list = request_data.getlist('required')
        save_list = request_data.getlist('save')
        if 'customfield_11603' in save_list:
            index = save_list.index('customfield_11603')
            save_list.insert(index + 1, u'customfield_11603_child')

        form_data = from_immutable_to_dict(request_data)

        for saved in save_list:
            temp = (field for field in fields_file if field['name'] == saved).next()
            if saved in required_list:
                temp['required'] = True
            if form_data[saved]:
                temp['default'] = form_data[saved]
            else:
                temp['default'] = ' '

            default.append(temp)

        default_template = TicketTemplate(guid=uuid.uuid1(), issuetype=issuetype, title='default_' + issuetype,
                                          user_id=user_id.get_id(),
                                          description='default template', json_form=json.dumps(default),
                                          project=form_data['project'])
        db.session.add(default_template)
        db.session.commit()
        return default_template.id

    elif user.role == 'USER':

        if kwargs.get('template_id', None) is not None:
            process = 'edit'
            template_id = kwargs.get('template_id')
        else:
            process = 'new'

        default_json = TicketTemplate.query.filter(TicketTemplate.title.like("default_" + issuetype) &
                                                   (TicketTemplate.issuetype == issuetype)).first()
        fields_db = json.loads(default_json.json_form)

        form_data = from_immutable_to_dict(request_data)
        for form_field in fields_db:
            # if form_field not in ('comment', 'title', 'description_template', 'resolved', 'time_spent'):
            if form_field['name'] in request_data: # form_data:
                temp = (field for field in fields_db if field['name'] == form_field['name']).next()
                if temp['default'] == ' ':
                    del temp['default']
                if (form_data[form_field['name']] != ' ') and (form_field['name'] != 'labels'):
                    temp['default'] = form_data[form_field['name']]
                elif form_field['name'] == 'labels':
                    temp['default'] = request_data.getlist('labels')
                default.append(temp)

                # {u'required': True, u'type': u'text', u'name': u'summary', u'label': u'Summary'}

        if form_data.get('resolved', None) == 'y':

            default.append({u'required': False, u'type': u'checkbox', u'name': u'resolved', u'label': u'Resolve issue',
                            u'default': form_data['resolved']})
        else:
            default.append({u'required': False, u'type': u'checkbox', u'name': u'resolved', u'label': u'Resolve issue'})

        if form_data.get('time_spent', None) != ' ':
            default.append({u'required': False, u'type': u'text', u'name': u'time_spent', u'label': u'Time spent',
                            u'default': form_data['time_spent']})
        else:
            default.append({u'required': False, u'type': u'text', u'name': u'time_spent', u'label': u'Time spent'})

        if form_data.get('comment', None):
            default.append({u'required': False, u'type': u'text', u'name': u'comment', u'label': u'Comment',
                            u'default': form_data['comment']})
        else:
            default.append({u'required': False, u'type': u'text', u'name': u'comment', u'label': u'Comment'})

        if process == 'new':
            user_template = TicketTemplate(guid=uuid.uuid1(), issuetype=issuetype, title=form_data['title'],
                                           description=form_data['description_template'], json_form=json.dumps(default),
                                           user_id=user_id.get_id(), project=default_json.project)
            db.session.add(user_template)
            db.session.commit()

            return user_template.id

        elif process == 'edit':
            user_template_edited = TicketTemplate.query.filter(TicketTemplate.guid == template_id).first()
            user_template_edited.title = form_data['title']
            user_template_edited.description = form_data['description_template']
            user_template_edited.json_form = json.dumps(default)
            db.session.commit()

            return user_template_edited.id
