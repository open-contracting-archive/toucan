from django import forms
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from ocdsmerge.util import get_tags


def _get_tags():
    return cache.get_or_set('git_tags', sorted(get_tags(), reverse=True), 3600)


def _get_extension_keys(data):
    for key in data:
        if key.startswith('extension_url_'):
            yield key


class OptionClassCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    template_name = 'default/widget/checkbox-multiple.html'
    option_template_name = 'default/widget/checkbox.html'


class MappingSheetOptionsForm(forms.Form):
    type = forms.ChoiceField(choices=(('select', _('Select a schema and version')),
                                      ('url', _('Provide a URL')),
                                      ('file', _('Upload a file')),
                                      ('extension', _('For an OCDS Extension'))),
                             initial='select',
                             error_messages={'required': _('Please choose an operation type')})
    select_url = forms.ChoiceField(required=False, label=_('Select a schema and version'),
                                   widget=forms.Select(attrs={'class': 'form-control'}),
                                   choices=(
                                       ('1.1', (
                                           ('https://standard.open-contracting.org/1.1/en/release-schema.json',
                                            '(1.1) Release'),
                                           ('https://standard.open-contracting.org/1.1/en/release-package-schema.json',
                                            '(1.1) Release Package'),
                                           ('https://standard.open-contracting.org/1.1/en/record-package-schema.json',
                                            '(1.1) Record Package')
                                       )
                                        ),
                                       ('1.1 (Español)', (
                                           ('http://standard.open-contracting.org/1.1/es/release-schema.json',
                                            '(1.1) (Español) Release'),
                                           ('http://standard.open-contracting.org/1.1/es/release-schema.json',
                                            '(1.1) (Español) Paquete de Release'),
                                           ('http://standard.open-contracting.org/1.1/es/record-package-schema.json',
                                            '(1.1) (Español) Paquete de Record')
                                       )
                                        ),
                                       ('1.0', (
                                           ('https://standard.open-contracting.org/schema/1__0__3/release-schema.json',
                                            '(1.0) Release'),
                                           ('https://standard.open-contracting.org/schema/'
                                            + '1__0__3/release-package-schema.json',
                                            '(1.0) Release Package'),
                                           ('https://standard.open-contracting.org/schema/'
                                            + '1__0__3/record-package-schema.json',
                                            '(1.0) Record Package'))
                                        )
                                   ))
    custom_url = forms.URLField(required=False, label=_('Provide the URL to a custom schema below'))
    custom_file = forms.FileField(required=False, label=_('Upload a file'))
    version = forms.ChoiceField(required=False, label=_('Please select an OCDS version'),
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
        # this method returns a list of BoundField and it is used in the template
        return list(filter(lambda field: field.name.startswith('extension_url_'), [field for field in self]))


class UnflattenOptionsForm(forms.Form):
    #id_schema
    schema = forms.ChoiceField(required=False,
                               label=_('Schema version'),
                               choices=(
                                   ('https://standard.open-contracting.org/1.1/en/release-schema.json',
                                    '1.1'),
                                   ('http://standard.open-contracting.org/1.1/es/release-schema.json',
                                    '1.1 (Español)'),
                                   ('https://standard.open-contracting.org/schema/1__0__3/release-schema.json',
                                    '1.0')),
                               widget=forms.Select(attrs={'class': 'form-control'}))
    output_format = forms.MultipleChoiceField(required=True,
                                              label=_('Output formats'),
                                              initial=('csv', 'xlsx'),
                                              choices=(('csv', 'CSV'),
                                                       ('xlsx', 'Excel')),
                                              widget=OptionClassCheckboxSelectMultiple(
                                                  attrs={'option_class': 'checkbox-inline'})
                                              )
    use_titles = forms.ChoiceField(required=True,
                                   label=_('Use titles instead of field names'),
                                   choices=((True, _('Yes')), (False, _('No'))),
                                   widget=forms.Select(attrs={'class': 'form-control'}),
                                   initial=False)
    filter_field = forms.CharField(required=False,
                                   help_text=_('Enter the field (top level fields only)'),
                                   widget=forms.TextInput(attrs={'class': 'form-control'}))
    filter_value = forms.CharField(required=False,
                                   help_text=_('Enter a value'),
                                   widget=forms.TextInput(attrs={'class': 'form-control'}))

    #id_preserve_fields
    preserve_fields = forms.MultipleChoiceField(required=False,
                                              label=_('Include ,the following fields only'),
                                              choices=(('ocid', 'OCID'),
                                                       ('id', 'ID'),
                                                       ('awa_ame_changes/ocid', 'awa_ame_changes/ocid')))
# forms.CharField(required=False,
#                                      label=_('Include the following fields only'),
#                                      widget=forms.Textarea(attrs={'class': 'form-control'}),
#                                      help_text=_('Enter the full path to each field, separated by a newline'))

    remove_empty_schema_columns = forms.ChoiceField(required=True,
                                                    label=_('Remove empty schema columns'),
                                                    choices=((True, _('Yes')), (False, _('No'))),
                                                    initial=False,
                                                    widget=forms.Select(attrs={'class': 'form-control'}))

    def show_schema_options(self):
        print(self.schema)

    def clean_output_format(self):
        return 'all' if len(self.cleaned_data['output_format']) > 1 else self.cleaned_data['output_format'][0]

    def clean_use_titles(self):
        return bool(not self.cleaned_data['use_titles'] == 'False')

    def clean_remove_empty_schema_columns(self):
        return bool(not self.cleaned_data['remove_empty_schema_columns'] == 'False')

    def clean(self):
        cleaned_data = super().clean()

        if bool(cleaned_data['filter_field']) ^ bool(cleaned_data['filter_value']):
            self.add_error('filter_field', _('Define both the field and value to filter data'))

    def non_empty_values(self):
        return {key: value for key, value in self.cleaned_data.items() if value}
