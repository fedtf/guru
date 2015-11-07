from django import template

register = template.Library()


@register.simple_tag
def project_users_works_now_style(project, user, date):
    if project.get_user_work_time(user, date)['working_now']:
        return 'background: #123600;'
    else:
        return ''
