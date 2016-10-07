#!/usr/bin/python


import wtforms.validators


class FieldHandler:
    def __init__(self, fields):
        self.formfields = {}
        print fields
        for field in fields:
            if field['name'] not in ('project', 'issuetype'):
                options = self.get_options(field)
                f = getattr(self, 'create_field_for_{}'.format(field['type']))(field, options)
                self.formfields[field['name']] = f

    def get_options(self, field):
        options = {'label': field['label']}
        if field['required'] is True:
            options['validators'] = [wtforms.validators.input_required()]
        if field.get('default'):
            options['default'] = field['default']
        return options

    def create_field_for_text(self, field, options):
        return wtforms.fields.StringField(**options)

    def create_field_for_textarea(self, field, options):
        return wtforms.fields.TextAreaField(**options)

    def create_field_for_integer(self, field, options):
        options['max_value'] = int(field.get("max_value", "999999999") )
        options['min_value'] = int(field.get("min_value", "-999999999") )
        return wtforms.fields.IntegerField(**options)

    def create_field_for_checkbox(self, field, options):
        return wtforms.fields.BooleanField(**options)

    def create_field_for_select(self, field, options):
        options['choices'] = [ (c['value'], c['name'] ) for c in field['choices'] ]
        return wtforms.fields.SelectField(**options)

    def create_field_for_multiselect(self, field, options):
        options['choices'] = [(c['value'], c['name']) for c in field['choices']]
        return wtforms.fields.SelectMultipleField(**options)


def get_form(jstr):
    fh = FieldHandler(jstr)
    return fh.formfields
    # return type('DynaForm', (Form,), fh.formfields )