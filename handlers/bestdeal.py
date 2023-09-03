from telebot import types
import requests
from datetime import date, timedelta
from telegram_bot_calendar import DetailedTelegramCalendar
from loader import bot
from states.states_classes import BestState
from api_seq.api import API, list_cities, make_api_request1, make_api_request
from universal_functions.functions import check_hotels
from keyboards.reply import pictures_question, calendar_part1, calendar_part2
from loguru import logger


@bot.message_handler(commands=['bestdeal'])
def bestdeal_selected(message: types.Message) -> None:
    """
        Initiates the BestState.location state when the /bestdeal command is selected.

        :param message: The message object representing the user's command.
        :type message: telebot.types.Message
        :return: None
    """
    bot.set_state(user_id=message.from_user.id, state=BestState.location, chat_id=message.chat.id)
    logger.info('Command /bestdeal. Starting state.')
    API.payload_list['resultsSize'] = 400
    API.payload_list['sort'] = "PRICE_LOW_TO_HIGH"
    with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
        data['command'] = message.text
    bot.send_message(chat_id=message.chat.id, text='Please enter a location:')


@logger.catch()
@bot.message_handler(state=BestState.location)
def bestdeal_location(message: types.Message) -> None:
    """
        Accepts the name of a city.
        Calls the list_cities function, which returns buttons with cities after making an API request.

        :param message: The message object representing the user's input.
        :type message: telebot.types.Message
        :return: None
    """
    list_cities(message=message, word='bestdeal')


@logger.catch()
@bot.callback_query_handler(func=lambda call: call.data.startswith('bestdeal'))
def bestdeal_request_hotels(call):
    """
        Processes a callback and saves the city ID.
        Prompts the user to enter the minimum price for the search.

        :param call: The callback object representing the user's interaction.
        :type call: telebot.types.CallbackQuery
        :return: None
    """
    region_id = call.data.strip('bestdeal')
    with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
        data['regionId'] = region_id
    API.payload_list['destination']['regionId'] = data['regionId']
    bot.set_state(user_id=call.from_user.id, state=BestState.minp, chat_id=call.message.chat.id)
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
    bot.send_message(chat_id=call.from_user.id, text='Please enter the minimum price for your search:')
    logger.info('Saving the city id and requesting the minimum price.')


@logger.catch()
@bot.callback_query_handler(func=lambda call: call.data.startswith('ireturn'))
def bestdeal_return(call):
    """
        Callback handler that requests the user to re-enter the location.

        :param call: The callback object representing the user's interaction.
        :type call: telebot.types.CallbackQuery
        :return: None
    """
    logger.info('Requesting to re-enter the location')
    bestdeal_selected(call.message)


@logger.catch()
@bot.message_handler(state=BestState.minp)
def bestdeal_minprice(message: types.Message) -> None:
    """
        Prompts the user to enter the maximum price for their search.

        :param message: The message object representing the user's input.
        :type message: telebot.types.Message
        :return: None
    """
    if message.text.isdigit():
        bot.send_message(chat_id=message.chat.id, text='Please enter the maximum price for your search:')
        bot.set_state(user_id=message.from_user.id, state=BestState.maxp, chat_id=message.chat.id)
        with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
            data['price_min'] = message.text
            API.payload_list['filters']['price']['min'] = int(data['price_min'])
        logger.info('Saving the minimum price')
    else:
        bot.send_message(chat_id=message.chat.id, text='Incorrect input. Please enter digits only:')


@logger.catch()
@bot.message_handler(state=BestState.maxp)
def bestdeal_maxprice(message: types.Message) -> None:
    """
        Checks that the entered maximum price is greater than the minimum.
        Prompts the user to enter the minimum distance from the center.

        :param message: The message object representing the user's input.
        :type message: telebot.types.Message
        :return: None
    """
    with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
        if message.text.isdigit():
            if int(message.text) > int(data['price_min']):
                bot.send_message(chat_id=message.chat.id, text='Please enter the minimum distance from center:')
                bot.set_state(user_id=message.from_user.id, state=BestState.mind, chat_id=message.chat.id)
                data['price_max'] = message.text
                API.payload_list['filters']['price']['max'] = int(data['price_max'])
                logger.info('Saving the maximum price')
            else:
                bot.send_message(chat_id=message.chat.id,
                                 text='The maximum cost should be greater than the minimum. Please re-enter:')
                logger.warning('Incorrect price range entered.')
        else:
            bot.send_message(chat_id=message.chat.id, text='Incorrect input. Please enter digits only:')


@logger.catch()
@bot.message_handler(state=BestState.mind)
def bestdeal_mindist(message: types.Message) -> None:
    """
        Prompts the user to enter the maximum distance from the center.

        :param message: The message object representing the user's input.
        :type message: telebot.types.Message
        :return: None
    """
    if message.text.isdigit():
        bot.send_message(chat_id=message.chat.id, text='Please enter the maximum distance from center:')
        bot.set_state(user_id=message.from_user.id, state=BestState.maxd, chat_id=message.chat.id)
        with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
            data['distance_min'] = message.text
        logger.info('Saving the minimum distance.')
    else:
        bot.send_message(chat_id=message.chat.id, text='Incorrect input. Please enter digits only:')


@logger.catch()
@bot.message_handler(state=BestState.maxd)
def bestdeal_maxdist(message: types.Message) -> None:
    """
        Checks that the entered maximum distance is greater than the minimum.
        Prompts the user to enter the number of hotel offers to display (maximum 7).

        :param message: The message object representing the user's input.
        :type message: telebot.types.Message
        :return: None
    """
    with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
        if message.text.isdigit():
            if int(message.text) > int(data['distance_min']):
                bot.send_message(chat_id=message.chat.id, text='How many hotel offers to display? (max 7):')
                bot.set_state(user_id=message.from_user.id, state=BestState.offers_count, chat_id=message.chat.id)
                data['distance_max'] = message.text
                logger.info('Saving the maximum distance.')
            else:
                bot.send_message(chat_id=message.chat.id,
                                 text='The maximum distance should be greater than the minimum. Please re-enter:')
                logger.warning('Invalid distance entered.')
        else:
            bot.send_message(chat_id=message.chat.id, text='Incorrect input. Please enter digits only:')


@logger.catch()
@bot.message_handler(state=BestState.offers_count)
def bestdeal_check_hotels(message: types.Message) -> None:
    """
        Accepts the number of hotels and passes it to the check_hotels_count function for input control.

        :param message: The message object representing the user's input.
        :type message: telebot.types.Message
        :return: None
    """
    check_hotels(message=message, state=BestState.clients_count)


@logger.catch()
@bot.message_handler(state=BestState.clients_count)
def bestdeal_start_calendar(message: types.Message) -> None:
    """
        If a valid number of people is entered, start processing the calendar.
        Calls the first part of the calendar, passing it the calendar ID.

        :param message: The message object representing the user's input.
        :type message: telebot.types.Message
        :return: None
    """
    if message.text.isdigit():
        bot.send_message(chat_id=message.chat.id, text='Please enter the check-in date:')
        calendar_part1(message, 5)
        with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
            data['people_count'] = message.text
            API.payload_list['rooms'][0]['adults'] = int(data['people_count'])
        logger.info('Saving the number of guests.')
    else:
        bot.send_message(chat_id=message.chat.id, text='Incorrect input. Please enter digits only:')


@logger.catch()
@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=5))
def bestdeal_handle_calendar(call):
    """
        Calls the second part of the calendar and gets the check-in date.
        Calls the first part of the calendar, passing it the ID to get the check-out date.
        Sets the min_date (API class).

        :param call: The callback object representing the user's interaction.
        :type call: telebot.types.CallbackQuery
        :return: None
    """
    res = calendar_part2(call, 5)
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
        calendar_part1(message=call.message, cal_id=6, min_date=API.min_date + timedelta(days=1),
                       max_date=API.min_date + timedelta(days=180))


@logger.catch()
@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=6))
def bestdeal_end_calendar(call):
    """
        Gets the check-out date and completes working with the calendar.
        Calculates the total number of days of stay.
        Sends a request to the user about the need for pictures.

        :param call: The callback object representing the user's interaction.
        :type call: telebot.types.CallbackQuery
        :return: None
    """
    res = calendar_part2(call, 6, min_date=API.min_date + timedelta(days=1),
                         max_date=API.min_date + timedelta(days=180))
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
        pic_markup = pictures_question('get3')
        bot.send_message(chat_id=call.from_user.id, text='Would you like to see pictures of the hotels?', reply_markup=pic_markup)


@logger.catch()
@bot.callback_query_handler(func=lambda call: call.data.startswith('get3'))
def bestdeal_photo_handler(call: types.CallbackQuery):
    """
        Handles the user's choice (whether photos are needed or not).
        Proceeds to the bestdeal_photos_question function for API request.

        :param call: The callback object representing the user's interaction.
        :type call: telebot.types.CallbackQuery
        :return: None
    """
    photos_needed = call.data == 'get3_yes'
    bestdeal_photos_question(call, photos_needed)


@logger.catch()
def bestdeal_photos_question(call, photos_needed):
    """
        Handles the user's response.
        Sends a request to the API through the make_api_request and make_api_request1 functions if photos are not needed.
        If photos are needed, changes the state and proceeds to the bestdeal_pictures_confirmed function.

        :param call: The callback object representing the user's interaction.
        :type call: telebot.types.CallbackQuery
        :param photos_needed: A boolean indicating whether photos are needed or not.
        :type photos_needed: bool
        :return: None
    """
    if photos_needed:
        bot.send_message(chat_id=call.message.chat.id, text='How many pictures to display for each offer? (max 3)')
        bot.set_state(user_id=call.from_user.id, state=BestState.pictures_count, chat_id=call.message.chat.id)
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
            id_price = dict()
            distance = list()
            for i in get_data:
                i['price']['options'][0]['formattedDisplayPrice'] = i['price']['options'][0][
                    'formattedDisplayPrice'].replace(',', '.') if ',' in i['price']['options'][0][
                    'formattedDisplayPrice'] else i['price']['options'][0]['formattedDisplayPrice']
            get_list = list(filter(lambda elem: is_hotel_in_range(elem, int(data['price_min']), int(data['price_max']),
                                                                  float(data['distance_min']),
                                                                  float(data['distance_max'])), get_data))
            if len(get_list) >= int(data['hotels_count']):
                length = int(data['hotels_count'])
            else:
                length = len(get_list)
                bot.send_message(call.message.chat.id, text=f'{length} offers found according to your filters.')
            for hotel in range(length):
                id_price[get_list[hotel]['id']] = get_list[hotel]['price']['options'][0]['formattedDisplayPrice']
                distance.append(get_list[hotel]['destinationInfo']['distanceFromDestination']['value'])
            make_api_request1(message=call.message, id_price=id_price, distance=distance, data=data,
                              user_id=call.from_user.id)
        bot.delete_state(call.from_user.id, call.message.chat.id)


@logger.catch()
@bot.message_handler(state=BestState.pictures_count)
def bestdeal_pictures_confirmed(message: types.Message) -> None:
    """
        Sends a request to the API through the make_api_request and make_api_request1 functions and displays hotels.

        :param message: The user's message.
        :type message: telebot.types.Message
        :return: None
    """
    if message.text.isdigit() and 0 < int(message.text) <= 3:
        with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
            data['pictures_question'] = message.text
        get_data = make_api_request()
        if not get_data:
            bot.send_message(chat_id=message.chat.id, text='Hotels are not found.')
            logger.error('Hotels are not found. Ending the state.')
        else:
            id_price = dict()
            distance = list()
            logger.info('Requesting API.')
            for i in get_data:
                i['price']['options'][0]['formattedDisplayPrice'] = i['price']['options'][0][
                    'formattedDisplayPrice'].replace(',', '.') if ',' in i['price']['options'][0][
                    'formattedDisplayPrice'] else i['price']['options'][0]['formattedDisplayPrice']
            get_list = list(filter(lambda elem: is_hotel_in_range(elem, int(data['price_min']), int(data['price_max']),
                                                                  float(data['distance_min']),
                                                                  float(data['distance_max'])), get_data))
            if len(get_list) >= int(data['hotels_count']):
                length = int(data['hotels_count'])
            else:
                length = len(get_list)
                bot.send_message(message.chat.id, text=f'{length} offers found according to your filters.')
            for hotel in range(length):
                id_price[get_list[hotel]['id']] = get_list[hotel]['price']['options'][0]['formattedDisplayPrice']
                distance.append(get_list[hotel]['destinationInfo']['distanceFromDestination']['value'])
            make_api_request1(message=message, id_price=id_price, distance=distance, data=data,
                              user_id=message.from_user.id)
        bot.delete_state(message.from_user.id, message.chat.id)
    else:
        bot.send_message(chat_id=message.chat.id, text='Incorrect input. Please enter digits only:')


def is_hotel_in_range(hotel, price_min, price_max, distance_min, distance_max):
    """
        Checks whether a hotel is within specified price and distance ranges.

        :param hotel: A dictionary containing hotel information.
        :type hotel: dict
        :param price_min: The minimum price.
        :type price_min: float
        :param price_max: The maximum price.
        :type price_max: float
        :param distance_min: The minimum distance to the destination.
        :type distance_min: float
        :param distance_max: The maximum distance to the destination.
        :type distance_max: float
        :return: True if the hotel is within the price and distance ranges, otherwise False.
        :rtype: bool
    """
    price = float(hotel['price']['options'][0]['formattedDisplayPrice'].strip('$'))
    distance = float(hotel['destinationInfo']['distanceFromDestination']['value'])
    return price_min <= price <= price_max and distance_min <= distance <= distance_max



