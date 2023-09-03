from loader import bot
from loguru import logger


@bot.message_handler(commands=['help'])
def help_user(message) -> None:
    """
    Function to end any user state and provide a list of available bot commands.

    :param message: The message object representing the user's command.
    :type message: telebot.types.Message
    :return: None
    """
    bot.delete_state(message.from_user.id, message.chat.id)
    text = """
    Bot commands:
    /lowprice - Get the cheapest hotels at the chosen location
    /highprice - Get the most expensive ones
    /bestdeal - Find the best deal by sorting by price and distance
    /history - Shows your search history
    """

    logger.info('Command /help')
    bot.send_message(message.chat.id, text=text)
