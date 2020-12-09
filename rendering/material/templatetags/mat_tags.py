from django import template

register = template.Library()

@register.filter
def spaces(value):
    s = value.replace('_', ' ')
    if 'by' in s:
        x = s.split(' by ')
        return x[0] + ' (by ' + x[1] + ')'
    return s
