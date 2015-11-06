from django.conf import settings

from telegram import Bot


telegram_bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
