from django import template

register = template.Library()

@register.filter
def dict_get(d, key):
    """Get a value from a dict in Django templates."""
    if d is None:
        return None
    return d.get(key)
