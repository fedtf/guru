from django import template
from django.utils.timesince import timesince
from datetime import datetime

register = template.Library()


def timedelta(value, arg=None):
    return ':'.join(str(value).split(':')[:3]).split('.')[0]

register.filter('timedelta',timedelta)