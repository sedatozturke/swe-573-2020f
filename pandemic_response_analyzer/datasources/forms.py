from django import forms

class DataSourceForm(forms.Form):
    platform = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder" : "Platform of source",                
                "class": "form-control"
            }
        ))
    source_type = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder" : "Type of source",                
                "class": "form-control"
            }
        ))
    tag = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder" : "Tag",                
                "class": "form-control"
            }
        ))
    source_key = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder" : "Covid, etc.",                
                "class": "form-control"
            }
        ))
    weight = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                "placeholder" : "1",                
                "class": "form-control"
            }
        ))