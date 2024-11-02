from csvFileParser.models import clubs
from django import forms

class TeamSelectionForm(forms.Form):
    clubs = forms.ModelMultipleChoiceField(
        queryset=clubs.objects.all().order_by('name'),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )