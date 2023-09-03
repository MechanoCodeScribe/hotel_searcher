from telebot import types
from telebot.custom_filters import StateFilter
from loader import bot
from utils.set_bot_commands import set_default_commands
from database.classes import db, User, Hotel
import handlers
from loguru import logger


@bot.message_handler()
def wrong_message(message: types.Message):
    """
        Handles incorrect user input.

        :param message: The message object representing the user's input.
        :type message: telebot.types.Message
        :return: None
    """
    if message.text:
        bot.send_message(message.from_user.id, text='Please enter /help to see bot commands.')


if __name__ == '__main__':
    """
        Starts the bot and handles commands.
    """
    logger.info('Start running')
    main_log_handler = logger.add("hotel_bot.log", rotation="100 MB", encoding='utf-8', level="INFO")
    error_log_handler = logger.add("errors.log", rotation="100 MB", encoding='utf-8', level="ERROR")
    set_default_commands(bot)
    bot.add_custom_filter(StateFilter(bot))
    if not User.table_exists() or not Hotel.table_exists():
        db.create_tables([User, Hotel])
    bot.infinity_polling()
