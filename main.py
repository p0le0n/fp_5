import configparser

import requests
import telebot

config = configparser.ConfigParser()
config.read('config.ini')

bot = telebot.TeleBot(config['DEFAULT']['TELEGRAM_TOKEN'])
telebot.logger.setLevel(telebot.logging.DEBUG)

def write_log(command):
    with open('logs.txt', 'a') as f:
        f.write(f'Successfully executed command: {command}\n')


@bot.message_handler(commands=['weather'])
def weather(message: telebot.types.Message):
    data = requests.get(
        'https://api.open-meteo.com/v1/forecast?latitude=59.93&longitude=30.31&current=temperature_2m,weather_code,wind_speed_10m').json()['current']

    temperature, weather_code, wind_speed = data['temperature_2m'], data['weather_code'], data['wind_speed_10m']

    description = ''
    if weather_code == 0:
        description = 'Clear sky'
    elif weather_code == 1:
        description = 'Mainly clear'
    elif weather_code == 2:
        description = 'Partly cloudy'
    elif weather_code == 3:
        description = 'Overcast'
    elif weather_code == 45:
        description = 'Fog '
    elif weather_code == 48:
        description = 'Rime'
    elif weather_code in [51, 53, 55, 56, 61, 63, 65, 66, 67]:
        description = 'Rain'
    elif weather_code == 77:
        description = 'Snow'
    elif weather_code in [80, 81, 82]:
        description = 'Shower'
    elif weather_code in [85, 86]:
        description = 'Snow shower'

    bot.send_message(
        message.chat.id,
        f'Temperature: {temperature}°C\nWind: {wind_speed}km/h\n{description}')

    write_log('/weather')


@bot.message_handler(commands=['currency'])
def exchange_rate(message: telebot.types.Message):
    data = requests.get(
        'https://iss.moex.com/iss/statistics/engines/currency/markets/selt/rates.json?iss.meta=off').json()

    usd = data['cbrf']['data'][0][3]
    eur = data['cbrf']['data'][0][6]

    bot.send_message(message.chat.id, f'RUB - USD: {usd}\nRUB - EUR: {eur}')

    write_log('/currency')

@bot.message_handler(commands=['ask'])
def ask(message: telebot.types.Message):
    question = (message.text or '').removeprefix('/ask ')

    data = requests.get(
        f'https://en.wikipedia.org/w/api.php?action=query&format=json&titles={question}&prop=extracts&explaintext&exintro').json()

    pages = data['query']['pages']

    first_page = next(iter(pages.keys()))

    content = (pages[first_page]['extract'].strip()
               if first_page != '-1' else None) or 'Formulate your question more specifically'

    bot.send_message(message.chat.id, content)

    write_log(f'/ask {question}')


@bot.message_handler(commands=['random_fact'])
def random_fact(message: telebot.types.Message):
    data = requests.get(
        'https://uselessfacts.jsph.pl/api/v2/facts/random').json()
    fact = data['text']
    bot.send_message(message.chat.id, fact)

    write_log('/random_fact')


@bot.message_handler(commands=['start', 'help'])
def start(message: telebot.types.Message):
    bot.send_message(
        message.chat.id,
        '/weather        - Current weather\n' +
        '/currency - Current exchange rate\n' +
        '/ask {about what} - Ask any question about something\n' +
        '/random_fact    - Random fact')

    write_log('/help or /start')


if __name__ == '__main__':
    bot.infinity_polling()
