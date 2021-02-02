from django import forms
from datasources.models import DataSource

class ReportForm(forms.Form):
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder" : "Report name",                
                "class": "form-control"
            }
        ))
    report_type_choices = [('Instant Report', 'Instant Report'), ('Trend Report', 'Trend Report')]
    report_type = forms.ChoiceField(
        choices=report_type_choices,
        widget=forms.Select(
            attrs={
                "placeholder" : "Report Type",                
                "class": "form-control"
            }
        ))
    tags = DataSource.objects.values('tag').distinct()
    tag_choices_arr = []
    for tag in tags:
        choice = (tag['tag'], tag['tag'])
        tag_choices_arr.append(choice)
    tag_choices = tag_choices_arr
    tag = forms.ChoiceField(
        choices=tag_choices,
        widget=forms.Select(
            attrs={
                "placeholder" : "Datasource Tag",                
                "class": "form-control"
            }
        ))