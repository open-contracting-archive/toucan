from django import template

from django.utils.translation import gettext as _

register = template.Library()

ALL_OPTIONS = [
    {'id': 'compile', 'value': '/compile/', 'text': _('Compile Releases')},
    {'id': 'split', 'value': '/split-packages/', 'text': _('Split Packages')},
    {'id': 'upgrade', 'value': '/upgrade/', 'text': _('Upgrade from 1.0 to 1.1')},
    {'id': 'convert', 'value': '/to-spreadsheet/', 'text': _('Convert to CSV/Excel')},
]


@register.inclusion_tag('default/tags/send_options_properties.html')
def show_options(options):
    """
    :param options: str list of options from templates. E.g. {% show_options "compile split upgrade convert" %}
    :return: the properties of the options to display
    """
    options_selected = []
    for option in ALL_OPTIONS:
        if option['id'] in options:
            options_selected.append(option)
    return {'options': options_selected}
