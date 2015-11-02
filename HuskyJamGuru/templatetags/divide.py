from django import template

register = template.Library()


@register.filter
def divide(value, arg):
    return int(value) // int(arg) if arg != 0 else 0
