from django import forms

class MappingSheetOptionsForm(forms.Form):
    url = forms.URLField(required=False,widget=forms.TextInput(attrs={'class': 'form-control'}))
    file = forms.FileField(required=False)
