import os
from datetime import datetime

from Project.settings import BASE_DIR

from HuskyJamGuru.models import PersonalDayWorkPlan


def version_description(request):
    with open(os.path.join(BASE_DIR, 'version.txt')) as f:
        VERSION_DESCRIPTION = f.read().strip()
    context_extras = {}
    context_extras['VERSION_DESCRIPTION'] = VERSION_DESCRIPTION

    return context_extras


def amount_of_planned_days(request):
    context_extras = {}
    if request.user.id:
        context_extras['AMOUNT_OF_PLANNED_DAYS'] = PersonalDayWorkPlan.get_amount_of_unceasingly_planned_days(
            request.user, datetime.today().date()
        )
        context_extras['PLAN_IS_FULFILLED'] = context_extras['AMOUNT_OF_PLANNED_DAYS'] >= 3
    return context_extras
