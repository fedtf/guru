from datetime import datetime, timedelta

from django.forms.models import inlineformset_factory
from django.forms import ModelForm, Form, ChoiceField

from .models import Project, WorkTimeEvaluation


class WorkTimeEvaluationForm(ModelForm):
    class Meta:
        model = WorkTimeEvaluation
        fields = ['type', 'time']


class ProjectForm(ModelForm):
    inlines = [
        WorkTimeEvaluationForm,
    ]

    class Meta:
        model = Project
        fields = ['name', 'work_start_date', 'deadline_date', 'issues_types']


ProjectFormSet = inlineformset_factory(
    Project,
    WorkTimeEvaluation,
    form=WorkTimeEvaluationForm,
    fields=('type', 'time',),
    extra=1
)


class PersonalPlanForm(Form):

    WORK_HOURS = (
        (None, 'Unscheduled'),
        (0, '0 hour'),
        (1, '1 hour'),
        (2, '2 hours'),
        (3, '3 hours'),
        (4, '4 hours'),
        (6, '6 hours'),
        (8, '8 hours'),
        (10, '10 hours'),
    )

    week = [
        'Monday',
        'Tuesday',
        'Wednesday',
        'Thursday',
        'Friday',
        'Saturday',
        'Sunday'
    ]

    def __init__(self, *args, **kwargs):
        super(PersonalPlanForm, self).__init__(*args, **kwargs)
        for i in range(7):
            date = datetime.date(datetime.now() + timedelta(days=i + 1))
            self.fields['day_%s' % i] = ChoiceField(
                choices=self.WORK_HOURS,
                label=self.week[date.weekday()] + ' (' + str(date) + ')',
                initial=None,
                required=False
            )
