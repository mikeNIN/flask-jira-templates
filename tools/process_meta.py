#!/usr/bin/python

"""
    process metadata and extract only data needed
    to create form; data types must be converted
    from jira to html
"""

import json
import os

from my_app import app


def get_labels(_labels_list):
    k = ['name', 'value']
    s = [{k[0]: i, k[1]: i} for i in _labels_list]
    return [{'name': " ", 'value': " "}] + s


def get_choices(_list):
    k = ['name', 'value']
    s = [{k[0]: i['value'], k[1]: i['value']} for i in _list]
    return [{'name': " ", 'value': " "}] + s


# def get_choices_cascade(_list):
#    k = ['name', 'value', 'child']
#    s = [{k[0]: i['value'], k[1]: i['value'], k[2]: [l['value'] for l in i['children']]} for i in _list]
#    return [{'name': "", 'value': "", 'child': []}] + s


def get_choices_customfield(_list):
    k = ['name', 'value']
    s = [{k[0]: i, k[1]: i} for i in _list]
    return [{'name': " ", 'value': " "}] + s


def process_files():
    # load separate file with data from customfield
    try:
        sr_cat = json.load(file('customfield_11603.json', 'r'))
        sorted_sr = sorted(sr_cat.keys(), key=lambda s: s.lower())
        allowed_values = get_choices_customfield(sorted_sr)
    except Exception as e:
        print e
        return False

    for filename in app.config['JIRA_ISSUE_TYPES']:
        try:
            with open(filename + '.json', 'r') as data_file:
                file_content = json.load(data_file)
            jira_fields = file_content['fields']
        except IOError as err:
            print err
            return False

        pass

        fields_list = []
        for key in jira_fields.iterkeys():
            if key != 'customfield_11603':
                val = []
                if not key.startswith('customfield'):
                    keys = ['name', 'label', 'required', 'type']
                    val.append(key)
                    val.append(jira_fields[key]['name'])
                    val.append(jira_fields[key]['required'])
                    if key == 'description':
                        val.append('textarea')
                        keys.append('max_length')
                        val.append('9999')
                    if key == 'labels':
                        val.append('multiselect')
                        keys.append('choices')
                        val.append(get_labels(app.config['LABELS_ALLOWED']))
                    else:
                        val.append('text')
                    if jira_fields[key]['schema']['type'] == 'user':
                        keys.append('id')
                        val.append(jira_fields[key]['name'])
                    fields_list.append(dict(zip(keys, val)))

                elif key.startswith('customfield'):
                    keys = ['name', 'label', 'required', 'type']
                    val.append(key)
                    val.append(jira_fields[key]['name'])
                    val.append(jira_fields[key]['required'])
                    if jira_fields[key]['schema']['type'] == 'user':
                        val.append('text')
                        keys.append('id')
                        val.append(jira_fields[key]['name'])
                    elif jira_fields[key]['schema']['custom'].endswith(':select') or jira_fields[key]['schema'][
                            'custom'].endswith(':multiselect'):
                        val.append('select')
                        keys.append('choices')
                        val.append(get_choices(jira_fields[key]['allowedValues']))
                    elif jira_fields[key]['schema']['custom'].endswith(':cascadingselect'):
                        pass
                    else:
                        val.append('text')
                    fields_list.append(dict(zip(keys, val)))
            elif key == 'customfield_11603':
                val = []
                keys = ['name', 'label', 'required', 'type']
                val.append(key)
                val.append(jira_fields[key]['name'])
                val.append(jira_fields[key]['required'])
                val.append('select')
                keys.append('choices')
                val.append(allowed_values)
                fields_list.append(dict(zip(keys, val)))

                # the same for cascade select
                val_1 = []
                keys_1 = ['name', 'label', 'required', 'type']
                val_1.append('customfield_11603_child')
                # print 'key', key
                val_1.append('Categories-SR-child')
                # print 'name', jira_fields[key]['name']
                val_1.append(False)
                # print 'required', jira_fields[key]['required']
                val_1.append('select')
                keys_1.append('choices')
                val_1.append([{"name": " ", "value": " "} , {"name": "Other", "value": "Other"}])
                # print main_sr
                fields_list.append(dict(zip(keys_1, val_1)))

        json.dump(fields_list, file(filename + '_default.json', 'w'), indent=4)
        os.remove(filename + '.json')


if __name__ == "__main__":
    process_files()
