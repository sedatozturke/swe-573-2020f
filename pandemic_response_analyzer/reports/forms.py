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
    report_type_choices = [('Instant Report', 'Instant Report')]
    report_type = forms.ChoiceField(
        choices=report_type_choices,
        widget=forms.Select(
            attrs={
                "placeholder" : "Report Type",                
                "class": "form-control"
            }
        ))
    tag = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder" : "Data source tag",                
                "class": "form-control"
            }
        ))