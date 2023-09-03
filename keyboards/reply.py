from loader import bot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from datetime import date, timedelta


def calendar_part1(message, cal_id, min_date=date.today(), max_date=date.today() + timedelta(days=180)):
    """
        Allows the user to select a year from a calendar.

        :param message: Message
        :param cal_id: int
        :param min_date: datetime (default: date.today())
        :param max_date: datetime (default: date.today() + timedelta(days=180))
        :return: None
    """
    calendar, step = DetailedTelegramCalendar(calendar_id=cal_id, min_date=min_date, max_date=max_date).build()

    bot.send_message(message.chat.id, 'Please select a year:', reply_markup=calendar)


def calendar_part2(call, cal_id, min_date=date.today(), max_date=date.today() + timedelta(days=180)):
    """
        Allows the user to select a month and day from a calendar.

        :param call: CallbackQuery
        :param cal_id: int
        :param min_date: datetime (default: date.today())
        :param max_date: datetime (default: date.today() + timedelta(days=180))
        :return: datetime if a date is selected, otherwise None
    """
    result, key, step = DetailedTelegramCalendar(calendar_id=cal_id, min_date=min_date, max_date=max_date).process(
        call.data)
    if not result and key and LSTEP[step] == 'month':
        bot.edit_message_text('Please select a month:', call.message.chat.id, call.message.message_id, reply_markup=key)
    elif not result and key and LSTEP[step] == 'day':
        bot.edit_message_text('Please select a day:', call.message.chat.id, call.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"Date selected: {result}", call.message.chat.id, call.message.message_id)
        return result


def pictures_question(get_id):
    """
        Create an inline keyboard with "Yes" and "No" buttons for user response.

        :param get_id: str (identifier used in the callback data)
        :return: InlineKeyboardMarkup
    """
    pictures_keyboard = InlineKeyboardMarkup()
    pictures_keyboard.add(InlineKeyboardButton(text='Yes', callback_data=get_id + '_yes'),
                          InlineKeyboardButton(text='No', callback_data=get_id + '_no'))
    return pictures_keyboard


def generate_city_keyboard(word, reply):
    """
        Creates a keyboard for selecting a city.

        :param reply: list
        :param word: str
        return: InlineKeyboardMarkup
    """
    city_keyboard = InlineKeyboardMarkup()
    for city_data in reply:
        city_name = city_data['regionNames']['fullName']
        callback_data = f'{word}{city_data["gaiaId"]}'
        city_keyboard.add(InlineKeyboardButton(text=city_name, callback_data=callback_data))
    if word == 'city_id':
        city_keyboard.add(InlineKeyboardButton(text='-Retry search-', callback_data='_return'))
    elif word == 'City_id':
        city_keyboard.add(InlineKeyboardButton(text='-Retry search-', callback_data='return'))
    else:
        city_keyboard.add(InlineKeyboardButton(text='-Retry search-', callback_data='ireturn'))
    return city_keyboard
