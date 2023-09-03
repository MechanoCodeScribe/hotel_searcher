from datetime import datetime
import json
from telebot import types
import telebot
import requests
from keyboards.reply import generate_city_keyboard
from database.classes import User, Hotel
from loader import API_KEY, bot
from loguru import logger


class API:
    """
    class contains the parameters for API requests
    """
    min_date = datetime.now()
    url1 = "https://hotels4.p.rapidapi.com/locations/v3/search"
    url2 = "https://hotels4.p.rapidapi.com/properties/v2/list"
    url3 = "https://hotels4.p.rapidapi.com/properties/v2/detail"

    # заголавок для url1
    headers_search = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    # заголавок для url2 и url3 они совпадают
    headers_list_detail = {
        "content-type": "application/json",
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    # полезная нагрузка для url2
    payload_list = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "destination": {"regionId": ""},
        "checkInDate": {
            "day": 0,
            "month": 0,
            "year": 0
        },
        "checkOutDate": {
            "day": 0,
            "month": 0,
            "year": 0
        },
        "rooms": [
            {
                "adults": 0
            }
        ],
        "resultsStartingIndex": 0,
        "resultsSize": 0,
        "sort": "PRICE_LOW_TO_HIGH",
        "filters": {"price": {
            "max": 20000,
            "min": 10
        }}
    }

    payload_detail = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "propertyId": ''
    }


def make_api_request():
    """
        Sends a request to the API and returns the response.

        :return: The response data in JSON format if successful, None otherwise.
        :rtype: dict or None
    """
    response = requests.request("POST", API.url2, json=API.payload_list, headers=API.headers_list_detail)
    response_data = response.json()
    if 'errors' in response_data and response_data['errors'][0]['message'].startswith(
            'Error occurred in downstream service.'):
        return None
    else:
        return response.json()['data']['propertySearch']['properties']


def make_api_request1(message, id_price, distance, data, user_id):
    """"
        Makes a request to the API and displays hotels based on the specified parameters.
        Records information about the command and the time of the request in the database.
        Records parameters in the database.

        :param message: Message
        :param id_price: dict
        :param distance: list
        :param data: dict
        :param user_id: int
        :return: None
    """

    index = 0
    total_days = data['total_days']

    user_record = User.create(command=data['command'], date=datetime.now().strftime('%d.%m.%Y - %H:%M:%S'),
                          user_id=user_id)
    for id_item, price in id_price.items():
        API.payload_detail['propertyId'] = id_item
        resp = requests.request("POST", API.url3, json=API.payload_detail, headers=API.headers_list_detail)

        try:
            resp_json = resp.json()

        except json.decoder.JSONDecodeError as e:
            print(f"Error decoding response JSON: {e}")
            continue

        if resp.status_code == 200 and resp_json and 'data' in resp_json and 'propertyInfo' in resp_json['data']:
            name = resp_json['data']['propertyInfo']['summary']['name']
            address = resp_json['data']['propertyInfo']['summary']['location']['address']['firstAddressLine']
            result_text = f'Link: https://hotels.com/h{id_item}.Hotel-Information\nName: {name}\nAddress: {address}\nCost per night: {price}\nTotal cost: ${int(price[1:]) * total_days}' \
                          f'\nDistance from center: {distance[index]}'
            Hotel.create(name=name, address=address, req=user_record)
            index += 1
            if data['pictures_question'] == 0:
                bot.send_message(message.chat.id, text=result_text)
            else:
                media_group = []
                images = resp_json['data']['propertyInfo']['propertyGallery']['images']
                for num in range(min(int(data['pictures_question']), len(images))):
                    photo = images[num]['image']['url']
                    caption = result_text if num == 0 else ''
                    media_group.append(types.InputMediaPhoto(photo, caption=caption))
                if media_group:
                    try:
                        bot.send_media_group(chat_id=message.chat.id, media=media_group)
                    except telebot.apihelper.ApiTelegramException as e:
                        for photo in media_group:
                            try:
                                bot.send_photo(chat_id=message.chat.id, photo=photo.media, caption=photo.caption)
                            except telebot.apihelper.ApiTelegramException:
                                pass
    logger.info('Saving to database')


@logger.catch()
def list_cities(message: types.Message, word) -> None:
    """
        Requests the entered city through the API, filtering user input.
        Calls the generate_city_keyboard function to create a keyboard with city choices.

        :param message: Message
        :param word: str
        :return: None
    """
    if message.text.isalpha():
        params = {'q': message.text.capitalize()}
        response = requests.request("GET", API.url1, headers=API.headers_search, params=params)
        reply = [city_data for city_data in response.json().get('sr', []) if city_data.get('type') == 'CITY']
        logger.info('Requesting API by location name')
        if reply:
            cit_keyboard = generate_city_keyboard(word=word, reply=reply)
            bot.send_message(chat_id=message.chat.id, text='Please choose the location:', reply_markup=cit_keyboard)
            logger.info('Displaying locations.')
        else:
            bot.send_message(chat_id=message.chat.id, text='Unknown location. Please re-enter:')
            logger.info('Unknown location entered.')
    else:
        bot.send_message(chat_id=message.chat.id, text='Incorrect input. Please enter letters only:')





