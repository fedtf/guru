from django import template
from django.utils.timezone import timedelta

register = template.Library()


@register.simple_tag
def project_users_work_times(project, user, date):
    work_time = project.get_user_work_time(user, date)
    if not work_time == timedelta():
        return ':'.join(str(work_time).split(':')[:2])
    else:
        return ''
