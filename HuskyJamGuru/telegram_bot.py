from django.core.exceptions import ObjectDoesNotExist

from telegram import Bot

from Project.settings import TELEGRAM_BOT_TOKEN
from .models import GitlabProject


class HuskyJamGuruBot(Bot):
    def send_notifications(self, webhook_info):
        webhook_type = webhook_info['object_kind']

        gitlab_project_id = webhook_info['object_attributes']['project_id']
        try:
            project = GitlabProject.objects.get(project_id=gitlab_project_id).project
        except ObjectDoesNotExist:
            with open('debug-log.txt', 'a') as f:
                print(gitlab_project_id, file=f)
                print(GitlabProject.objects.values_list('project_id', flat=True), file=f)

        message_text = ''
        if webhook_type == 'note':
            message = ('There is a new comment from {} in the {} '
                       'of the project {}: "{}". You can respond here: {}.')
            if webhook_info['object_attributes']['noteable_type'] == 'Issue':
                noteable = 'issue "{}"'.format(webhook_info['issue']['title'])
            else:
                noteable = 'merge request'
            message_text = message.format(webhook_info['user']['name'],
                                          noteable,
                                          project.name,
                                          webhook_info['object_attributes']['note'],
                                          webhook_info['object_attributes']['url'])
        elif webhook_type == 'issue':
            action = webhook_info['object_attributes']['action']
            webhook_type = 'issue_close' if action == 'close' else 'issue_create'
            message_text = ('Issue "{}" from project {} has been {} by {}. '
                            'You can find it here: {}.'.format(webhook_info['object_attributes']['title'],
                                                               project.name,
                                                               'closed' if action == 'close' else 'created',
                                                               webhook_info['user']['name'],
                                                               webhook_info['object_attributes']['url']))
        elif webhook_info == 'push':
            message_text = ('A new push to the project {} came from {}.').format(project.name,
                                                                                 webhook_info['user']['name'])
        if message_text:
            for user in set(access.user for access in project.user_project_accesses.all()):
                try:
                    telegram_user = user.telegram_user
                except ObjectDoesNotExist:
                    continue
                if telegram_user.notification_enabled and webhook_type in telegram_user.notification_events:
                    telegram_bot.sendMessage(chat_id=telegram_user.telegram_id, text=message_text)


telegram_bot = HuskyJamGuruBot(token=TELEGRAM_BOT_TOKEN)
