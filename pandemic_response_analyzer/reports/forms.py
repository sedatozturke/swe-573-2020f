from django import forms

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
    tags = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder" : "Data source tags",                
                "class": "form-control"
            }
        ))