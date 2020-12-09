from django import template

register = template.Library()

@register.filter
def join_ids(obj_list, sep):
    return sep.join([str(el.id) for el in obj_list])

@register.filter
def join_names(obj_list, sep):
    return sep.join([el.name for el in obj_list])

@register.filter
def dict_get(obj, field):
    return obj[str(field)] if str(field) in obj else 0

@register.simple_tag
def queue(obj):
  return obj.filter(running__isnull=False)

@register.filter
def size_Mb(obj):
    try:
        return f"{int(obj>>10)} Mb"
    except:
        return "no data"

