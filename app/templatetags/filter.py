from django import template

register = template.Library()

@register.filter
def display_backslash_n(value):
    return value.replace("X", "&#92;n")