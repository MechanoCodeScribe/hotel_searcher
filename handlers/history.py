from telebot import types
from loader import bot
from database.classes import User, Hotel
from loguru import logger


@logger.catch()
@bot.message_handler(commands=['history'])
def get_db(message: types.Message) -> None:
    """
    Retrieves information from the database and sends it to the chat.

    :param message: The message object representing the user's command.
    :type message: telebot.types.Message
    :return: None
    """
    logger.info('Command /history.')
    if not User.select().where(User.user_id == message.from_user.id):
        bot.send_message(message.chat.id, text='Data not found')
        logger.error('User history not found')
    for user in User.select().where(User.user_id == message.from_user.id):
        bot.send_message(chat_id=message.chat.id, text=f'Command: {user.command}\nDate of search: {user.date}\nHotels:')

        for hotel in Hotel.select().where(Hotel.req == user.id):
            bot.send_message(chat_id=message.chat.id, text=f'Name: {hotel.name}\nAddress: {hotel.address}')

