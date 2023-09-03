from telebot import types
from loader import bot
from loguru import logger


@bot.message_handler(commands=['start'])
def start(message: types.Message) -> None:
    """
    Handler for the /start command, resets the user's state.

    :param message: The message object representing the user's command.
    :type message: telebot.types.Message
    :return: None
    """
    bot.delete_state(message.from_user.id, message.chat.id)
    logger.info('Command /start.')

    bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAIOAmTzyzFZCaDHtp26eViYaUXK5uowAAKoAgACnNbnCoCh_glxM4XJMAQ')
    bot.send_message(message.chat.id, text='Welcome to ENJOY TOURS agency! Please enter /help to see bot commands.')
