from django import forms
from datasources.models import DataSource

class CrawlerForm(forms.Form):
    datasource_id = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                "placeholder" : "Datasource Id",                
                "class": "form-control"
            }
        ))