
from django import forms
from csvFileParser.models import game, streaming_package, streaming_offer

class BookFilterForm(forms.Form):
    category = forms.ModelChoiceField(queryset=game.objects.all(), required=True, label="Category")
    author = forms.ModelChoiceField(queryset=streaming_offer.objects.all(), required=True, label="Author")
    publisher = forms.ModelChoiceField(queryset=streaming_package.objects.all(), required=True, label="Publisher")