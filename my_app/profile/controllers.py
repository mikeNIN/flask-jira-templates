#!/usr/bin/python

import json

from flask import (
    render_template, g, request, Blueprint, redirect, url_for,
    flash
)
from flask.ext.login import login_required, current_user
from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import InputRequired, Regexp

from my_app import app, jira_conn
from my_app.auth.models import TicketTemplate, Users
from my_app.ticket_template import dynaform

from tools.process_form_request import process_all
from tools.test import create_ticket_jira

# Define the blueprint: 'profile'
profile = Blueprint('profile', __name__, template_folder='templates',
                    static_folder='static')


def debug(text):
    print text
    return ''


# environment.filters['debug']=debug

app.jinja_env.filters['debug'] = debug


# Set the route and accepted methods
@profile.before_request
def before_request():
    g.user = current_user


@profile.route('/my_templates')
@login_required
def templates_list():
    u_id = g.user.get_id()
    templates_list_user = TicketTemplate.query.filter_by(user_id=u_id).all()
    if len(templates_list_user) == 0:
        return render_template('profile.html', step='list')
    else:
        return render_template('profile.html', templates_user=templates_list_user, step='list')


# route tickets archive
@profile.route('/created_tickets')
@login_required
def tickets_archive():
    if jira_conn.connection():

        print jira_conn.connection().search_issues('assignee = {0}'.format(g.user.username))
    else:
        print 'some problem'
    return render_template('profile.html', step='archive')


@profile.route('/my_templates/<template_id>', methods=['GET', 'POST'])
@login_required
def open_template(template_id):
    # open template to create ticket
    chosen_template = TicketTemplate.query.filter_by(guid=template_id).first()
    chosen_template_json = json.loads(chosen_template.json_form)
    chosen_template_dict = dynaform.get_form(chosen_template_json)

    class TemplateForm(Form):
        pass

    for template_form in chosen_template_dict:
        setattr(TemplateForm, template_form, chosen_template_dict.get(template_form))

    form = TemplateForm(request.form)
    form_issuetype = chosen_template.issuetype
    form_title = chosen_template.title
    form_project = chosen_template.project
    step = 'open'

    if request.method == 'POST':
        if form.validate_on_submit():
            create_ticket_jira(request.form, issuetype=form_issuetype, project=form_project)
            return redirect(url_for('profile.templates_list'))
        else:
            flash('there were errors processing your request', 'error')
    return render_template('create_edit.html', **locals())


@profile.route('/my_templates/edit/<template_id>', methods=['GET', 'POST'])
@login_required
def edit_template(template_id):
    chosen_template = TicketTemplate.query.filter_by(guid=template_id).first()
    chosen_template_json = json.loads(chosen_template.json_form)

    for element in chosen_template_json:
        if element['required'] is True:
            if element.get('default', None) is None:
                element.update({'default': ' '})

    chosen_template_dict = dynaform.get_form(chosen_template_json)

    form_title = chosen_template.title
    form_description = chosen_template.description

    class TemplateForm(Form):
        pass

    TemplateForm.title = StringField('Name of template', [InputRequired()], default=form_title)
    TemplateForm.description_template = StringField('Short Description of template', [InputRequired()],
                                                    default=form_description)
    for template_form in chosen_template_dict:
        setattr(TemplateForm, template_form, chosen_template_dict.get(template_form))

    form = TemplateForm(request.form)
    form_issuetype = chosen_template.issuetype
    form_project = chosen_template.project
    step = 'edit'

    if request.method == 'POST':
        if form.validate_on_submit():
            print request.form
            process_all(request.form, g.user, form_issuetype, template_id=template_id)
            return redirect(url_for('profile.open_template', template_id=template_id))
        else:
            flash('there were errors processing your request', 'error')
    return render_template('create_edit.html', **locals())

    # @profile.route()
