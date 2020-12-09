from django import template
register = template.Library()
#from .models import Product

@register.simple_tag
def natures(obj, partname):
    return obj.usedNatures(partname)


@register.simple_tag(takes_context=True)
def greeting(context):
    return "Hello {0}!".format(context['request'].user.first_name)
