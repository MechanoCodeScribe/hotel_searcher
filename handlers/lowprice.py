from telebot import types
import requests
from datetime import date, timedelta
from telegram_bot_calendar import DetailedTelegramCalendar
from loader import bot
from states.states_classes import LowState
from api_seq.api import API, list_cities, make_api_request1, make_api_request
from universal_functions.functions import check_hotels
from keyboards.reply import pictures_question, calendar_part1, calendar_part2
from loguru import logger   


@bot.message_handler(commands=['lowprice'])
def lowprice_selected(message: types.Message) -> None:
    """
        Initiates the LowState.location state when the /lowprice command is selected.

        :param message: The message object representing the user's command.
        :type message: telebot.types.Message
        :return: None
    """
    bot.set_state(user_id=message.from_user.id, state=LowState.location, chat_id=message.chat.id)
    API.payload_list['filters']['price']['min'] = 10
    API.payload_list['filters']['price']['max'] = 30000
    API.payload_list['sort'] = "PRICE_LOW_TO_HIGH"
    logger.info('Command /lowprice. Starting state.')
    with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
        data['command'] = message.text
    bot.send_message(chat_id=message.chat.id, text='Please enter a location:')


@logger.catch()
@bot.message_handler(state=LowState.location)
def lowprice_location(message: types.Message) -> None:
    """
        Accepts the name of a city.
        Calls the list_cities function, which returns buttons with cities after making an API request.

        :param message: The message object representing the user's input.
        :type message: telebot.types.Message
        :return: None
    """
    list_cities(message=message, word='city_id')


@logger.catch()
@bot.callback_query_handler(func=lambda call: call.data.startswith('city_id'))
def lowprice_request_hotels(call):
    """
        Processes a callback and saves the city ID.
        Prompts the user to enter the number of hotel offers to display (maximum 7).

        :param call: The callback object representing the user's interaction.
        :type call: telebot.types.CallbackQuery
        :return: None
    """
    region_id = call.data.strip('city_id')
    with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
        data['regionId'] = region_id
    API.payload_list['destination']['regionId'] = data['regionId']
    bot.set_state(user_id=call.from_user.id, state=LowState.offers_count, chat_id=call.message.chat.id)
    bot.send_message(chat_id=call.from_user.id, text='How many hotel offers to display? (max 7):')
    logger.info('Saving the city id and requesting the number of offers.')


@logger.catch()
@bot.callback_query_handler(func=lambda call: call.data.startswith('_return'))
def lowprice_return(call):
    """
        Callback handler that requests the user to re-enter the location.

        :param call: The callback object representing the user's interaction.
        :type call: telebot.types.CallbackQuery
        :return: None
    """
    logger.info('Requesting to re-enter the location.')
    lowprice_selected(call.message)


@logger.catch()
@bot.message_handler(state=LowState.offers_count)
def lowprice_check_hotels(message: types.Message) -> None:
    """
        Accepts the number of hotels and passes it to the check_hotels_count function for input control.

        :param message: The message object representing the user's input.
        :type message: telebot.types.Message
        :return: None
    """
    check_hotels(message=message, state=LowState.clients_count)


@logger.catch()
@bot.message_handler(state=LowState.clients_count)
def lowprice_start_calendar(message: types.Message) -> None:
    """
        If a valid number of people is entered, start processing the calendar.
        Calls the first part of the calendar, passing it the calendar ID.

        :param message: The message object representing the user's input.
        :type message: telebot.types.Message
        :return: None
    """
    if message.text.isdigit():
        bot.send_message(chat_id=message.chat.id, text='Please enter the check-in date:')
        calendar_part1(message, 1)
        with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
            data['people_count'] = message.text
            API.payload_list['rooms'][0]['adults'] = int(data['people_count'])
            API.payload_list['resultsSize'] = int(data['hotels_count'])
        logger.info('Saving the number of guests.')
    else:
        bot.send_message(chat_id=message.chat.id, text='Incorrect input. Please enter digits only:')


@logger.catch()
@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def lowprice_handle_calendar(call):
    """
        Calls the second part of the calendar and gets the check-in date.
        Calls the first part of the calendar, passing it the ID to get the check-out date.
        Sets the min_date (API class).

        :param call: The callback object representing the user's interaction.
        :type call: telebot.types.CallbackQuery
        :return: None
    """
    res = calendar_part2(call, 1)
    if res:
        date_list = str(res).split('-')
        with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
            data['date_in'] = {'d': date_list[2], 'm': date_list[1], 'y': date_list[0]}
            data['date_check_in'] = res
            API.min_date = date(int(data['date_in']['y']), int(data['date_in']['m']), int(data['date_in']['d']))
            API.payload_list['checkInDate']['day'] = int(data['date_in']['d'])
            API.payload_list['checkInDate']['month'] = int(data['date_in']['m'])
            API.payload_list['checkInDate']['year'] = int(data['date_in']['y'])
        logger.info('Saving the check-in date.')
        bot.send_message(chat_id=call.from_user.id, text='Please enter the check-out date:')
        calendar_part1(message=call.message, cal_id=2, min_date=API.min_date + timedelta(days=1), max_date=API.min_date + timedelta(days=180))


@logger.catch()
@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
def lowprice_end_calendar(call):
    """
        Gets the check-out date and completes working with the calendar.
        Calculates the total number of days of stay.
        Sends a request to the user about the need for pictures.

        :param call: The callback object representing the user's interaction.
        :type call: telebot.types.CallbackQuery
        :return: None
    """
    res = calendar_part2(call, 2, min_date=API.min_date + timedelta(days=1), max_date=API.min_date + timedelta(days=180))
    if res:
        date_list = str(res).split('-')
        with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
            data['date_out'] = {'d': date_list[2], 'm': date_list[1], 'y': date_list[0]}
            data['date_check_out'] = res
            delta = data['date_check_out'] - data['date_check_in']
            data['total_days'] = delta.days
            API.payload_list['checkOutDate']['day'] = int(data['date_out']['d'])
            API.payload_list['checkOutDate']['month'] = int(data['date_out']['m'])
            API.payload_list['checkOutDate']['year'] = int(data['date_out']['y'])
        logger.info('Saving the check-out date and requesting if pictures needed.')
        pic_markup = pictures_question('get1')
        bot.send_message(chat_id=call.from_user.id, text='Would you like to see pictures of the hotels?', reply_markup=pic_markup)


@logger.catch()
@bot.callback_query_handler(func=lambda call: call.data.startswith('get1'))
def lowprice_photo_handler(call: types.CallbackQuery):
    """
        Handles the user's choice (whether photos are needed or not).
        Proceeds to the lowprice_photos_question function for API request.

        :param call: The callback object representing the user's interaction.
        :type call: telebot.types.CallbackQuery
        :return: None
    """
    photos_needed = call.data == 'get1_yes'
    lowprice_photos_question(call, photos_needed)


@logger.catch()
def lowprice_photos_question(call, photos_needed):
    """
        Handles the user's response.
        Sends a request to the API through the make_api_request and make_api_request1 functions if photos are not needed.
        If photos are needed, changes the state and proceeds to the lowprice_pictures_confirmed function.

        :param call: The callback object representing the user's interaction.
        :type call: telebot.types.CallbackQuery
        :param photos_needed: A boolean indicating whether photos are needed or not.
        :type photos_needed: bool
        :return: None
    """
    if photos_needed:
        bot.send_message(chat_id=call.message.chat.id, text='How many pictures to display for each offer? (max 3)')
        bot.set_state(user_id=call.from_user.id, state=LowState.pictures_count, chat_id=call.message.chat.id)
        logger.info('User needs pictures')
    else:
        logger.info('No need of pictures. Requesting API.')
        with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
            data['pictures_question'] = 0
        get_data = make_api_request()
        if not get_data:
            bot.send_message(chat_id=call.message.chat.id, text='Hotels are not found.')
            logger.error('Hotels are not found. Ending the state.')
        else:
            id_price = {hotel['id']: hotel['price']['options'][0]['formattedDisplayPrice'] for hotel in get_data}
            distance = [hotel['destinationInfo']['distanceFromDestination']['value'] for hotel in get_data]
            make_api_request1(message=call.message, id_price=id_price, distance=distance, data=data,
                              user_id=call.from_user.id)
        bot.delete_state(call.from_user.id, call.message.chat.id)


@logger.catch()
@bot.message_handler(state=LowState.pictures_count)
def lowprice_pictures_confirmed(message: types.Message) -> None:
    """
        Initiates API requests and displays hotels based on user preferences, including picture count.

        :param message: The user's message containing the desired number of pictures to display.
        :type message: types.Message
        :return: None
    """
    if message.text.isdigit() and 0 < int(message.text) <= 3:
        with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
            data['pictures_question'] = message.text
        get_data = make_api_request()
        logger.info('Requesting API.')
        if not get_data:
            bot.send_message(chat_id=message.chat.id, text='Hotels are not found.')
            logger.error('Hotels are not found. Ending the state.')
        else:
            id_price = {hotel['id']: hotel['price']['options'][0]['formattedDisplayPrice'] for hotel in get_data}
            distance = [hotel['destinationInfo']['distanceFromDestination']['value'] for hotel in get_data]
            make_api_request1(message=message, id_price=id_price, distance=distance, data=data, user_id=message.from_user.id)
        bot.delete_state(message.from_user.id, message.chat.id)
    else:
        bot.send_message(chat_id=message.chat.id, text='Incorrect input. Please enter digits only:')


