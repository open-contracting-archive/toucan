import json

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.inclusion_tag('default/tags/schema_as_ul_main.html', takes_context=True)
def get_schema_as_ul(context, schema):
    return {'schema': schema, 'omitDeprecated': context['omitDeprecated']}


@register.filter()
def items_method(value):
    """
    A workaround to call the 'items' method in an object (a dictionary is expected).

    :param value: a python dictionary
    :return:
    """
    return value.items()


@register.inclusion_tag("default/tags/jstree-data.html", takes_context=True)
def jstree_data(context, obj_name, obj_def):
    data = {}
    if not context['prefix']:
        data['selected'] = True
    if 'properties' in obj_def.keys() or ('items' in obj_def.keys() and 'properties' in obj_def['items'].keys()):
        data['icon'] = 'glyphicon glyphicon-th-list'
    else:
        data['icon'] = 'glyphicon glyphicon-minus'

    if context['required']:
        if obj_name in context['required']:
            data['disabled'] = True
    return data


@register.filter()
def get_path(key, prefix):
    if not prefix:
        return key
    return prefix + '/' + key
