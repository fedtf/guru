from django import template

register = template.Library()


@register.simple_tag
def project_users_work_times(project, user, date):
    return project.get_user_work_time(user, date)
