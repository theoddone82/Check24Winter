
from django import forms
from csvFileParser.models import game, streaming_package, streaming_offer, clubs, lieges

class BookFilterForm(forms.Form):
    clubs = forms.ModelChoiceField(
        queryset=clubs.objects.all(),  # Or apply any filters if needed
        required=False,
        empty_label="Select a Category..."  # This sets the placeholder
    )    
    lieges = forms.ModelChoiceField(
        queryset=lieges.objects.all(),  # Or apply any filters if needed
        required=False,
        empty_label="Select a liege..."  # This sets the placeholder
    )    