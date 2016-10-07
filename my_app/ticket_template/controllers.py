#!/usr/bin/python

import json

from flask import (
    render_template, g, request, Blueprint,
    redirect, url_for, flash, session
)
from flask_wtf import Form
from flask.ext.login import login_required, current_user
from wtforms import StringField, BooleanField, SelectField
from wtforms.validators import InputRequired, Regexp

from my_app import app, lm
import dynaform
from my_app.auth.models import Users, TicketTemplate
from tools.process_form_request import process_all

# Define the blueprint: 'template_jira'
template_jira = Blueprint('ticket_template', __name__, template_folder='templates',
                          static_folder='static')


@lm.user_loader
# Given *user_id*, return the associated User object.
def load_user(id):
    return Users.query.get(int(id))


# Set the route and accepted methods
@template_jira.before_request
def before_request():
    if current_user.is_authenticated:
        g.user = current_user  # return username in get_id()
    else:
        g.user = None  # or 'some fake value', whatever


@template_jira.route('/create_template/<step>', methods=['GET', 'POST'])
@login_required
def create_template(step):
    if not request.script_root:
        request.script_root = url_for('index', _external=True)

    class PickIssueType(Form):
        issue_type_select = SelectField('IssueType', [InputRequired()],
                                        choices=[(element, element) for element in
                                                 app.config['JIRA_ISSUE_TYPES']])

    if step == 'choose':

        user = Users.query.filter_by(id=g.user.get_id()).first()

        session['type'] = ''
        form = PickIssueType()
        if form.validate_on_submit():
            session['type'] = request.form['issue_type_select']
            return redirect(url_for('.create_template', step='process'))
        return render_template('user_template.html', form=form, step='choose')

    if step == 'process':

        # get from database default json
        default_template = TicketTemplate.query.filter(TicketTemplate.title.like("default_" + session['type'])).first()

        # source json for dynaform class
        fields = json.loads(default_template.json_form)
        jira_dict_user = dynaform.get_form(fields)
        project = ''
        issuetype = default_template.issuetype

        for field in fields:
            if field['name'] == 'project':
                project = field['default']

        sr_categories = None
        try:
            sr_categories = json.load(file(app.config['BASE_DIR'] + '/tools/customfield_11603', 'r'))
        except Exception as e:
            print e.message

        if sr_categories is None:
            pass

        class UserTemplate(Form):
            pass

        UserTemplate.resolved = BooleanField('Resolve issue', default=False)
        # needed regexp to check if string is in format (3w 2d 12h 5m)
        # UserTemplate.time_spent = StringField('Time spent', [Regexp(), InputRequired()])
        UserTemplate.time_spent = StringField('Time spent', [InputRequired()], default=' ')
        UserTemplate.comment = StringField('Comment')
        UserTemplate.title = StringField('Name of template', [InputRequired()])
        UserTemplate.description_template = StringField('Short Description of template', [InputRequired()])
        for name in jira_dict_user:
            setattr(UserTemplate, name, jira_dict_user.get(name))

        form = UserTemplate(request.form)
        formdata = None
        sr_all = sr_categories
        step = 'process'
        project = project
        issuetype = issuetype

        if request.method == 'POST':
            if form.validate_on_submit():
                # import ipdb
                # ipdb.set_trace()
                process_all(request.form, g.user, session['type'])
                return redirect(url_for('profile.templates_list'))
            else:
                flash('there were errors processing your request', 'error')
        return render_template("user_template.html", **locals())
