from csvFileParser.models import clubs, lieges
from django import forms

class TeamSelectionForm(forms.Form):
    clubs = forms.ModelMultipleChoiceField(
        queryset=clubs.objects.all().order_by('-score'),
        required=False,
    )

    lieges = forms.ModelMultipleChoiceField(
        queryset=lieges.objects.all().order_by('-score'),
        required=False,
    )
