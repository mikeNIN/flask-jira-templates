from ldap3 import SUBTREE, ALL_ATTRIBUTES

from flask import jsonify, request
from flask.ext.wtf import Form
from wtforms import widgets, SelectMultipleField, SubmitField

from my_app import app, ldap_ac





@app.route('/_search_user')
def search_ldap_user():
    print 'search user'
    user = request.args.get('in_string', '', type=str)
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

    return jsonify(result=result_dict)
