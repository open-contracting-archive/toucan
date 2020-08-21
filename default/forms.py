from django import forms
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _

from default.util import ocds_tags


def _get_extension_keys(data):
    for key in data:
        if key.startswith('extension_url_'):
            yield key


class MappingSheetOptionsForm(forms.Form):
    type = forms.ChoiceField(choices=(('select', _('Select a schema and version')),
                                      ('url', _('Provide a URL')),
                                      ('file', _('Upload a file')),
                                      ('extension', _('For an OCDS Extension'))),
                             initial='select',
                             error_messages={'required': _('Please choose an operation type')})
    select_url = forms.URLField(required=False, label=_('Select a schema and version'))
    custom_url = forms.URLField(required=False, label=_('Provide the URL to a custom schema below'))
    custom_file = forms.FileField(required=False, label=_('Upload a file'))
    version = forms.ChoiceField(required=False, label=_('Please select an OCDS version'),
                                choices=[(tag, tag.replace('__', '.')) for tag in ocds_tags()],
                                widget=forms.Select(attrs={'class': 'form-control'}))

    def __init__(self, query=None, *args, **kwargs):
        super().__init__(query, *args, **kwargs)
        if query:
            for key in _get_extension_keys(query):
                self.fields[key] = forms.URLField(required=False)
        else:
            self.fields['extension_url_0'] = forms.URLField(required=False, initial='')

    def clean(self):
        if super().is_valid():
            type_selected = self.cleaned_data.get('type')
            extension_keys = list(_get_extension_keys(self.cleaned_data))

            if type_selected == 'select':
                if not self.cleaned_data.get('select_url'):
                    self.add_error('select_url', forms.ValidationError(_('Please select an option')))
            elif type_selected == 'url':
                if not self.cleaned_data.get('custom_url'):
                    self.add_error('custom_url', forms.ValidationError(_('Please provide a URL')))
            elif type_selected == 'file':
                if not self.cleaned_data.get('custom_file'):
                    self.add_error('custom_file', forms.ValidationError(_('Please provide a file')))
            elif type_selected == 'extension':
                if not extension_keys:
                    raise forms.ValidationError(_('Provide at least one extension URL'))

            self.cleaned_data['extension_urls'] = [self.cleaned_data[key] for key in extension_keys]

    def get_extension_fields(self):
        # this method returns a list of BoundField and it is used in the template
        return list(filter(lambda field: field.name.startswith('extension_url_'), [field for field in self]))
