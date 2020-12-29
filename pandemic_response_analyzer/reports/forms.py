from django import forms

class ReportForm(forms.Form):
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder" : "Report name",                
                "class": "form-control"
            }
        ))
    tags = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder" : "Data source tags",                
                "class": "form-control"
            }
        ))