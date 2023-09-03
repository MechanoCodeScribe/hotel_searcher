from loader import bot
from loguru import logger


def check_hotels(message, state):
    """
        Checks if the number of hotels requested is not greater than the maximum (7).
        Prompts the user to enter the number of persons.
        :param message: The message object representing the user's input.
        :param state: The state to set for the user after processing.
        :return: None
    """
    if message.text.isdigit() and 0 < int(message.text) <= 7:
        bot.send_message(chat_id=message.chat.id, text='Enter the number of persons:')
        bot.set_state(user_id=message.from_user.id, state=state, chat_id=message.chat.id)
        with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
            data['hotels_count'] = message.text
        logger.info('Saving the number of hotels requested.')

    else:
        bot.send_message(chat_id=message.chat.id, text='Incorrect input. Please enter digit from 1 to 7:')



