from django import forms

class DataSourceForm(forms.Form):
    platform_choices = [('Reddit', 'Reddit')]
    platform = forms.ChoiceField(
        choices=platform_choices,
        widget=forms.Select(
            attrs={
                "placeholder" : "Platform of source",                
                "class": "form-control"
            }
        ))
    source_type_choices = [('Subreddit', 'Subreddit')]
    source_type = forms.ChoiceField(
        choices=source_type_choices,
        widget=forms.Select(
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
                "placeholder" : "Enter a number",                
                "class": "form-control"
            }
        ))