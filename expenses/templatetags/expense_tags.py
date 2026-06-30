from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dict by key in templates."""
    return dictionary.get(key)

@register.filter
def split(value, delimiter=','):
    """Split a string by delimiter."""
    return value.split(delimiter)

@register.filter
def floatformat_ar(value, arg=0):
    """Format a number with commas."""
    try:
        return f"{float(value):,.{int(arg)}f}"
    except (ValueError, TypeError):
        return value
