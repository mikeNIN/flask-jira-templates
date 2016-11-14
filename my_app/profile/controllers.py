#!/usr/bin/python

import json

from ldap3 import SUBTREE

from flask import (
    render_template, g, request, Blueprint, redirect, url_for,
    flash, session, jsonify
)
from flask.ext.login import login_required, current_user
from flask_wtf import Form
from wtforms import StringField, SelectField, BooleanField, IntegerField
from wtforms.validators import InputRequired

from my_app import app, jira_conn, lm, ldap_ac
from my_app.auth.models import TicketTemplate, Users
from utils import dynaform
from utils.process_form_request import process_all
from utils.test import create_ticket_jira

# Define the blueprint: 'profile'
profile = Blueprint('profile', __name__, template_folder='templates',
                    static_folder='static', static_url_path=app.config['BASE_DIR'] + '/my_app/profile')



@lm.user_loader
# Given *user_id*, return the associated User object.
def load_user(id):
    return Users.query.get(int(id))


# Set the route and accepted methods
@profile.before_request
def before_request():
    if current_user.is_authenticated:
        g.user = current_user  # return username in get_id()
    else:
        g.user = None  # or 'some fake value', whatever




@profile.route('/my_templates')
@login_required
def templates_list():
    if not request.script_root:
        request.script_root = url_for('index', _external=True)
    u_id = g.user.get_id()
    templates_list_user = TicketTemplate.query.filter_by(user_id=u_id).all()
    if len(templates_list_user) == 0:
        return render_template('profile.html', attr=app.config['AD_ATTR'])
    else:
        return render_template('profile.html', templates_user=templates_list_user,
                               attr=app.config['AD_ATTR'])


# route tickets archive
@profile.route('/created_tickets')
@login_required
def tickets_archive():
    if jira_conn.connection():
        print "ok"
        # print jira_conn.connection().search_issues('assignee = {0}'.format(g.user.username))
    else:
        print 'some problem'
    return render_template('archive.html', step='archive')


@profile.route('/my_templates/<template_id>', methods=['GET', 'POST'])
@login_required
def open_template(template_id):
    # open template to create ticket
    chosen_template = TicketTemplate.query.filter_by(guid=template_id).first()
    chosen_template_json = json.loads(chosen_template.json_form)
    chosen_template_dict = dynaform.get_form(chosen_template_json)

    sr_categories = None
    try:
        sr_categories = json.load(file(app.config['BASE_DIR'] + '/utils/customfield_11603.json', 'r'))
    except Exception as e:
        print e.message

    if sr_categories is None:
        pass

    class TemplateForm(Form):
        pass

    for template_form in chosen_template_dict:
        setattr(TemplateForm, template_form, chosen_template_dict.get(template_form))

    form = TemplateForm(request.form)
    form_issuetype = chosen_template.issuetype
    form_title = chosen_template.title
    form_project = chosen_template.project
    attr = app.config['AD_ATTR']
    sr_all = json.dumps(sr_categories)

    if request.method == 'POST':
        if form.validate_on_submit():
            create_ticket_jira(request.form, issuetype=form_issuetype, project=form_project)
            return redirect(url_for('profile.templates_list'))
        else:
            flash('there were errors processing your request', 'error')
    return render_template('open_template.html', **locals())


@profile.route('/my_templates/edit/<template_id>', methods=['GET', 'POST'])
@login_required
def edit_template(template_id):
    chosen_template = TicketTemplate.query.filter_by(guid=template_id).first()
    chosen_template_json = json.loads(chosen_template.json_form)

    for element in chosen_template_json:
        if element['required'] is True:
            if element.get('default', None) is None:
                element.update({'default': ' '})

    sr_categories = None
    try:
        sr_categories = json.load(file(app.config['BASE_DIR'] + '/utils/customfield_11603.json', 'r'))
    except Exception as e:
        print e

    if sr_categories is None:
        pass

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
    sr_all = json.dumps(sr_categories)

    if request.method == 'POST':
        if form.validate_on_submit():
            print request.form
            process_all(request.form, g.user, form_issuetype, template_id=template_id)
            return redirect(url_for('profile.open_template', template_id=template_id))
        else:
            flash('there were errors processing your request', 'error')
    return render_template('edit_template.html', **locals())


@profile.route('/create_template/<step>', methods=['GET', 'POST'])
@login_required
def create_template(step):
    if not request.script_root:
        request.script_root = url_for('index', _external=True)

    class PickIssueType(Form):
        issue_type_select = SelectField('IssueType', [InputRequired()],
                                        choices=[(element, element) for element in
                                                 app.config['JIRA_ISSUE_TYPES']])

    sr_categories = None
    try:
        sr_categories = json.load(file(app.config['BASE_DIR'] + '/utils/customfield_11603.json', 'r'))
    except Exception as e:
        print e.message

    if sr_categories is None:
        pass

    if step == 'choose':

        user = Users.query.filter_by(id=g.user.get_id()).first()

        session['type'] = ''
        form = PickIssueType()
        if form.validate_on_submit():
            session['type'] = request.form['issue_type_select']
            return redirect(url_for('.create_template', step='process'))
        return render_template('user_template.html', form=form, step='choose', sr_all=sr_categories)

    if step == 'process':

        # get from database default json
        default_template = TicketTemplate.query.filter(
            TicketTemplate.title.like("default_" + session['type'])).first()

        # source json for dynaform class
        fields = json.loads(default_template.json_form)
        jira_dict_user = dynaform.get_form(fields)
        project = ''
        issuetype = default_template.issuetype

        for field in fields:
            if field['name'] == 'project':
                project = field['default']

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
                process_all(request.form, g.user, session['type'])
                return redirect(url_for('profile.templates_list'))
            else:
                flash('there were errors processing your request', 'error')
        return render_template("user_template.html", **locals())


@profile.route('/_search_user', methods=['POST'])
def search_ldap_user():
    response = request.get_json()
    user = response['username']
    search_base = app.config['LDAP_GLOBAL_FILTER']

    search_filter = '(&' + search_base + '(|(sn={0})(sn={0}*)(cn={0}*)(cn=*{0})(givenName={0})))'.format(user)
    connection = ldap_ac.connection
    results = connection.extend.standard.paged_search(search_base=app.config['LDAP_BASE_DN'],
                                                      search_filter=search_filter,
                                                      search_scope=SUBTREE,
                                                      attributes=app.config['AD_ATTR_RAW'])
    result_dict = {}
    while True:
        try:
            # while data in results
            res = results.next()
            # take DN data
            dn_key = res['dn']
            # take 'raw_attributes' from res dict
            raw_attr = res['raw_attributes']
            # append dict to list
            key = dn_key.split('=')[1][:-3]
            dict_value = {k: v[0] if v else '' for k, v in raw_attr.items()}
            result_dict[key] = dict_value
        except StopIteration:
            break
    print result_dict
    return jsonify(result=result_dict)