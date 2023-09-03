# Telegram Hotel Search Bot

![Python](https://img.shields.io/badge/python-v3.8%2B-blue)

Telegram bot for hotel search that finds hotels based on three main search criteria: searching for the cheapest hotels in a location, the most expensive hotels, and the best deals based on price and distance from the city center. Please note that this bot does not make hotel reservations as it uses a test version of an API.

## Installation and Usage

1. Obtain your Telegram bot token.
2. Get the Hotels API key from [RapidAPI](https://www.rapidapi.com).
3. In the project folder, create the .env file, and insert your bot token and API key into the respective fields.
4. Ensure you have Python 3.8 or higher installed.
5. Open the terminal from the project folder.
6. Install the dependencies using the following command:
    ```bash
    pip install -r requirements.txt
    ```
7. Start your Telegram bot by running:
    ```bash
    python main.py
    ```

## Commands

1. `/start` - Begin interacting with the bot.
2. `/help` - Get assistance and view the list of available commands.
3. `/lowprice` - Search for the cheapest hotels.
4. `/highprice` - Search for the most expensive hotels.
5. `/bestdeal` - Search for the best deals based on price and distance from the center.
6. `/history` - Display the search history.

## Dependencies

1. [certifi](https://pypi.org/project/certifi/) - 2023.7.22
2. [charset-normalizer](https://pypi.org/project/charset-normalizer/) - 3.2.0
3. [idna](https://pypi.org/project/idna/) - 3.4
4. [peewee](https://pypi.org/project/peewee/) - 3.16.2
5. [pyTelegramBotAPI](https://pypi.org/project/pyTelegramBotAPI/) - 4.12.0
6. [python-dateutil](https://pypi.org/project/python-dateutil/) - 2.8.2
7. [python-dotenv](https://pypi.org/project/python-dotenv/) - 1.0.0
8. [python-telegram-bot-calendar](https://pypi.org/project/python-telegram-bot-calendar/) - 1.0.5
9. [requests](https://pypi.org/project/requests/) - 2.31.0
10. [six](https://pypi.org/project/six/) - 1.16.0
11. [urllib3](https://pypi.org/project/urllib3/) - 1.26.16
12. [loguru](https://pypi.org/project/loguru/) - 0.7.0

---

*Please note that this bot uses a test version of an API and does not handle hotel reservations. It is intended for demonstration purposes.*


