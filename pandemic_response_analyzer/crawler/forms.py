from django import forms
from datasources.models import DataSource

class CrawlerForm(forms.Form):
    datasources = DataSource.objects.all()
    choices = []
    for datasource in datasources:
        source_text = datasource.platform + "." + datasource.source_type + "." + datasource.source_key
        choice = (datasource.id, source_text)
        choices.append(choice)
    datasource_id = forms.ChoiceField(
        choices=choices,
        widget=forms.Select(
            attrs={
                "placeholder" : "Datasource",                
                "class": "form-control"
            }
        ))