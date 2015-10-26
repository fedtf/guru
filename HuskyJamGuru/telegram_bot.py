from Project.settings import TELEGRAM_BOT_TOKEN

from twx.botapi import TelegramBot

telegam_bot = TelegramBot(TELEGRAM_BOT_TOKEN)
telegam_bot.update_bot_info().wait()
