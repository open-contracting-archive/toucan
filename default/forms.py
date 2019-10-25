from django import forms
from django.utils.translation import gettext as _

TYPE_CHOICES = (('select', 'Select a Schema'),
                ('url', 'Provide an URL'),
                ('file', 'Upload a file'),
                ('extension', 'For an OCDS Extension'))


class MappingSheetOptionsForm(forms.Form):
    type = forms.ChoiceField(choices=TYPE_CHOICES, error_messages={'required': _('Please choose an operation type')})
    select_url = forms.URLField(required=False)
    custom_url = forms.URLField(required=False)
    custom_file = forms.FileField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if len(args) > 0:
            extension_urls_keys = list(filter(lambda key: key.startswith('extension_url_'), args[0]))
            for key in extension_urls_keys:
                self.fields[key] = forms.URLField(required=False)
        else:
            self.fields['extension_url_0'] = forms.URLField(required=False, initial="")

    def clean(self):
        if super().is_valid():
            type_selected = self.cleaned_data.get('type')

            if type_selected == 'select':
                if 'select_url' not in self.cleaned_data or self.cleaned_data['select_url'] == '':
                    self.add_error('select_url', forms.ValidationError(_('Please select an option')))
            elif type_selected == 'url':
                if 'custom_url' not in self.cleaned_data or self.cleaned_data['custom_url'] == '':
                    self.add_error('custom_url', forms.ValidationError(_('Please provide an URL')))
            elif type_selected == 'file':
                if 'custom_file' not in self.cleaned_data or not self.cleaned_data['custom_file']:
                    self.add_error('custom_file', forms.ValidationError(_('Please provide a file')))
            elif type_selected == 'extension':
                extension_keys = list(filter(lambda key: key.startswith('extension_url_'), self.cleaned_data.keys()))
                if not extension_keys:
                    raise forms.ValidationError(_('Provide at least one extension URL'))
                for key in extension_keys:
                    if not self.cleaned_data[key]:
                        self.add_error(key, _('Please provide an URL'))
            else:
                raise forms.ValidationError(_('Please select an option'))

            extension_urls_keys = list(filter(lambda name: name.startswith('extension_url_'), self.cleaned_data))
            self.cleaned_data['extension_urls'] = [self.cleaned_data[key] for key in extension_urls_keys]

    def get_extension_fields(self):
        return list(filter(lambda field: field.name.startswith('extension_url_'), [field for field in self]))
