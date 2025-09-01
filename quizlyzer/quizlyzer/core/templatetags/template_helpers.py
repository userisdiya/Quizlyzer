from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    try:
        key = int(key)
    except (ValueError, TypeError):
        return None
    return dictionary.get(key)