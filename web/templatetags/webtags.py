from django import template

register = template.Library()

@register.filter
def absolute(value):
    if value == '': return ''
    return abs(value)
