from ldap3 import SUBTREE, ALL_ATTRIBUTES

from flask.ext.wtf import Form
from wtforms import widgets, SelectMultipleField, SubmitField

from my_app import app, ldap_ac


def get_attr():
    with app.app_context():
        connection = ldap_ac.connection
        entry_generator = connection.extend.standard.paged_search(search_base=app.config['LDAP_BASE_DN'],
                                                                  search_filter=app.config['LDAP_GLOBAL_FILTER'],
                                                                  search_scope=SUBTREE,
                                                                  attributes=ALL_ATTRIBUTES,
                                                                  size_limit=1)
        for entry in entry_generator:
            result = entry['attributes'].keys()

        return sorted(result)


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class SimpleForm(Form):
    list_of_attr = get_attr()
    # create a list of value/description tuples
    attr = [(x, x) for x in list_of_attr]
    attr_form = MultiCheckboxField('Attributes', choices=attr)
    submit = SubmitField(u'Select')