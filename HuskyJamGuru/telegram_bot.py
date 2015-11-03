import logging
import time

from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from telegram import Bot
from celery.contrib.methods import task_method

from .models import GitlabProject
from Project.celery import app


logger = logging.getLogger(__name__)


class HuskyJamGuruBot(Bot):
    def send_notifications(self, webhook_info):
        webhook_type = webhook_info['object_kind']

        if webhook_type == 'push':
            gitlab_project_id = webhook_info['project_id']
        else:
            gitlab_project_id = webhook_info['object_attributes']['project_id']

        try:
            project = GitlabProject.objects.get(gitlab_id=gitlab_project_id).project
        except ObjectDoesNotExist:
            logger.info('Got webhook with unexisting project id: {}'.format(gitlab_project_id))
            return

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

    @app.task(filter=task_method)
    def change_user_notification_state(self, new_state, telegram_user):
        if new_state == 'disabled':
            telegram_user.notification_enabled = False
            telegram_user.save()
        elif new_state == 'enabled':
            for i in range(10):
                time.sleep(4)
                for update in self.getUpdates():
                    if telegram_user.telegram_id in update.message.text:
                        telegram_user.telegram_id = update.message.from_user.id
                        telegram_user.notification_enabled = True
                        telegram_user.save()
                        return
            logger.info('Failed trying to subscribe user {} with id {}'.format(telegram_user,
                                                                               telegram_user.telegram_id))


telegram_bot = HuskyJamGuruBot(token=settings.TELEGRAM_BOT_TOKEN)
