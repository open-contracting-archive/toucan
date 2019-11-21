from django import forms
from django.core.cache import cache
from django.utils.translation import gettext as _
from ocdsmerge.merge import get_tags


def _get_tags():
    return cache.get_or_set('git_tags', sorted(get_tags(), reverse=True), 3600)


def _get_extension_keys(data):
    for key in data:
        if key.startswith('extension_url_'):
            yield key


class MappingSheetOptionsForm(forms.Form):
    type = forms.ChoiceField(choices=(('select', 'Select a Schema'),
                                      ('url', 'Provide a URL'),
                                      ('file', 'Upload a file'),
                                      ('extension', 'For an OCDS Extension')),
                             error_messages={'required': _('Please choose an operation type')})
    select_url = forms.URLField(required=False)
    custom_url = forms.URLField(required=False)
    custom_file = forms.FileField(required=False)
    version = forms.ChoiceField(required=False,
                                choices=[(tag, tag.replace('__', '.')) for tag in _get_tags()],
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
        return _get_extension_keys(field.name for field in self)
