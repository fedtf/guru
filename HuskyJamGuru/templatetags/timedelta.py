from django import template

register = template.Library()


def timedelta(value, arg=None):
    return ':'.join(str(value).split(':')[:3]).split('.')[0]

register.filter('timedelta', timedelta)
