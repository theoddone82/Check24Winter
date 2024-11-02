# custom_filters.py

from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None  # Return None if the dictionary is invalid or the key doesn't exist
