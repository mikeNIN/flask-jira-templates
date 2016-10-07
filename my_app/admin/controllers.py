#!/usr/bin/python

import collections
import json

from flask import render_template, g, request, Blueprint, redirect, url_for
from flask_login import login_required, current_user, login_user, flash, logout_user, session
from flask_wtf import Form
from wtforms import SelectField, StringField, SelectMultipleField
from wtforms.validators import InputRequired

from my_app import lm, bcrypt, db, app
from my_app.auth.forms import LoginForm
from my_app.auth.models import Users, TicketTemplate
from my_app.ticket_template import dynaform

from tools.process_form_request import process_all

# Define the blueprint: 'admin'
admin = Blueprint('admin', __name__, template_folder='templates', static_folder='static')


# Set the route and accepted methods
@admin.before_request
def before_request():
    if current_user.is_authenticated:
        g.user = current_user  # return username in get_id()
    else:
        g.user = None  # or 'some fake value', whatever


@lm.user_loader
def load_user(id):
    return Users.query.get(int(id))


@admin.route('/admin', methods=['GET', 'POST'])
@admin.route('/admin/', methods=['GET', 'POST'])
def admin_login():
    # If sign in form is submitted
    if g.user is None or not g.user.is_admin():
        form = LoginForm(request.form)
        if form.validate_on_submit():
            user = Users.query.filter_by(username=form.login_name.data).first()
            if user and user.is_admin() and bcrypt.check_password_hash(user.passwd, form.password_field.data):
                user.authenticated = True
                db.session.add(user)
                db.session.commit()
                login_user(user)
                return redirect(url_for('admin.template_wizard', step='list'))
            flash("Username or Password is invalid", 'error')
        return render_template('admin_login.html', form=form)
    else:
        return redirect(url_for('admin.template_wizard', step='list'))


@admin.route('/admin/logout', methods=['GET'])
@login_required
def admin_logout():
    logout_user()
    return render_template('admin_logout.html')


@admin.route('/admin/template/<step>', methods=['GET', 'POST'])
@login_required
def template_wizard(step):

    if step == 'choose':

        template_types = TicketTemplate.query.all()
        templates_present = [i.issuetype for i in template_types]

        class PickIssueType(Form):
            issue_type = SelectField('IssueType', [InputRequired()],
                                     choices=[(element, element) for element in
                                              app.config['JIRA_ISSUE_TYPES'] if
                                              element not in templates_present])

        session['type'] = ''
        form = PickIssueType()
        if form.validate_on_submit():
            session['type'] = request.form['issue_type']
            return redirect(url_for('.template_wizard', step='process'))
        return render_template('admin_template.html', form=form, step='choose')

    if step == 'process':

        def get_dicts_admin(type_of_issue):
            with open(app.config['JIRA_SOURCE_FILES'][type_of_issue], 'r') as data_file:
                fields = json.load(data_file)
            json_form = fields
            return dynaform.get_form(json_form)

        jira_dict_admin = get_dicts_admin(session['type'])

        # class definitions
        class BaseFormAdmin(Form):
            def __iter__(self):
                ordered_fields = collections.OrderedDict()
                for element in getattr(self, 'field_order', []):
                    ordered_fields[element] = self._fields.pop(element)
                ordered_fields.update(self._fields)
                self._fields = ordered_fields
                return super(BaseFormAdmin, self).__iter__()

        class NewFormAdmin(BaseFormAdmin):
            pass

        # NewFormAdmin.resolved = BooleanField('Resolve issue')
        # NewFormAdmin.comment = StringField('Comment')
        for name in jira_dict_admin:
            setattr(NewFormAdmin, name, jira_dict_admin.get(name))

        class FormDefault(NewFormAdmin):
            project = StringField('Project', default='ITS')
            issuetype = StringField('Issuetype', default=session['type'])
            summary = StringField('Summary')
            labels = SelectMultipleField('Labels', choices=[(c[0], c[1]) for c in jira_dict_admin.get(
                'labels').kwargs['choices']], render_kw={'size': 3})
            customfield_10802 = SelectField('Reporting department',
                                            choices=[(c[0], c[1]) for c in jira_dict_admin.get(
                                                'customfield_10802').kwargs['choices']])
            customfield_11603 = SelectField('Categories-SR', choices=[(c[0], c[1]) for c in jira_dict_admin.get(
                'customfield_11603').kwargs['choices']])

            customfield_11603_child = SelectField('Categories-SR-child',
                                                  choices=[(c[0], c[1]) for c in jira_dict_admin.get(
                                                      'customfield_11603_child').kwargs['choices']])
            assignee = StringField('Assignee')
            reporter = StringField('Reporter')
            customfield_11600 = StringField('Requester')
            description = StringField('Description')
            field_order = ('project', 'summary', 'issuetype', 'labels', 'customfield_10802', 'assignee', 'reporter',
                           'customfield_11600', 'customfield_11603', 'customfield_11603_child', 'description')

        form = FormDefault(request.form)
        print request.form
        step = 'process'
        formdata = None
        if request.method == 'POST':
            if form.validate_on_submit():
                flash('processing and saving your form to database', 'message')
                process_all(request.form, g.user, session['type'])
                return redirect(url_for('admin.template_wizard', step='list'))
            else:
                flash('there were errors processing your request', 'error')
        return render_template('admin_template.html', **locals())

    if step == 'list':
        template_list = TicketTemplate.query.filter(TicketTemplate.title.like("default_%")).all()
        return render_template('admin_template.html', step='list', all=template_list)


@admin.route('/admin/synchro/', methods=['GET', 'POST'])
@login_required
def synchronize():
    pass
