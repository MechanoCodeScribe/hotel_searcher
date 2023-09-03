from telebot.types import BotCommand
from config_data.config import DEFAULT_COMMANDS


def set_default_commands(bot):
    """
        Sets the default commands for the bot's menu.

        :param bot: The TeleBot instance for which default commands are to be set.
        :type bot: telebot.TeleBot
        :return: None
    """
    bot.set_my_commands(
        [BotCommand(*i) for i in DEFAULT_COMMANDS]
    )
