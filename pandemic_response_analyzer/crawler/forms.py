from django import forms

class CrawlerForm(forms.Form):
    datasource_id = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                "placeholder" : "Datasource Id",                
                "class": "form-control"
            }
        ))