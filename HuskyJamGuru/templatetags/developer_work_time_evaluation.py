from django import template
from HuskyJamGuru.models import PersonalDayWorkPlan

register = template.Library()


@register.simple_tag(takes_context=True)
def developer_work_time_evaluation(context, project, user, date):
    result = ''
    work_plan = PersonalDayWorkPlan.get_work_plan(user, date, date)
    if len(work_plan) > 0:
        result = str(work_plan[0].work_hours) + ':00/' + str(context['projects_per_user_amount'][user])
    return result
