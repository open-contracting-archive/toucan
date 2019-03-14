from django import forms

class MappingSheetOptionsForm(forms.Form):
    version = forms.CharField()
