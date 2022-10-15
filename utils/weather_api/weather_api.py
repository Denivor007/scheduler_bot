from pprint import pprint
import datetime
import requests
from google_trans_new import google_translator
from config import *
import unicodedata

weather_emoji = {
    "drizzle":"☔",
    "thermometer" : "🌡",
    "clear sky": "🌞",
    "few clouds": "🌤",
    "scattered clouds": "⛅",
    "broken clouds": "🌥",
    "overcast clouds": "☁",
    "light thunderstorm": "🌩",
    "thunderstorm": "🌩",
    "heavy thunderstorm": "🌩",
    "ragged thunderstorm": "🌩",
    "thunderstorm with light rain": "⛈",
    "thunderstorm with rain": "⛈",
    "thunderstorm with heavy rain": "⛈",
    "thunderstorm with light drizzle": "⛈",
    "thunderstorm with drizzle": "⛈",
    "thunderstorm with heavy drizzle": "⛈",
    "rain": "🌧",
    "snow": "🌨",
    "fog" : "🌫",
    "mist": "🌫",
    "smoke": "🌫",
    "haze": "🌫",
    "Sand": "🌫",
    "dust": "🌫",
    "ash": "🌋",
    "squall": "💨",
    "tornado": "🌪",
}

Translator = google_translator()


def get_smile(temp):
    if temp >= 27:
        return "🥵"
    if 27 > temp > 0:
        return "☺"
    if temp <= 0:
        return "🥶"


def city_checker(city, open_weather_token = open_weather_token):
    city = city.replace(" ", "")
    print(f"city = \"{city}\"")
    r = requests.get(
        f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={open_weather_token}&units=metric"
    )
    data = r.json()
    if data['cod'] == "404":
        return False

    return True


def get_weather(city, open_weather_token = open_weather_token):
        city = city.replace(" ","")

        r = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={open_weather_token}&units=metric"
        )
        data = r.json()
        print(f"city = \"{city}\"")
        pprint(data)
        city = data["name"]
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        sunrise = data["sys"]["sunrise"]
        sunrise = datetime.datetime.fromtimestamp(sunrise).time()
        sunset = data["sys"]["sunset"]
        sunset = datetime.datetime.fromtimestamp(sunset).time()
        clouds = data["clouds"]["all"]
        description = data["weather"][0]["description"]
        main = data["weather"][0]["main"].lower()
        emoji = weather_emoji.get(description, weather_emoji.get(main))
        wind_speed = data["wind"]["speed"]
        wind_gust = data["wind"].get("gust", wind_speed)

        city_t = Translator.translate(city, lang_src='en', lang_tgt='uk')
        description_t = Translator.translate(description, lang_src='en', lang_tgt='uk')

        message = f"{city_t}:\n" \
                  f"{emoji} За вікном сьогодні {description_t}\n" \
                  f"🌇 Світанок та захід сонця:<i>{sunrise} - {sunset}</i>\n" \
                  f"🌡 Температура повітря {temp}℃, відчувається як {feels_like}℃ {get_smile(feels_like)}\n" \
                  f"💨 Вітер дмухає зі швидкістю {wind_speed} м\\с, пориви сягають {wind_gust}" \

        if data["sys"]["country"] == "UA":
            message += "\nCлава Україні🇺🇦"
        if data["sys"]["country"] == "RU":
            message += "\nпутінський режим все-ще знищує економіку цього міста"

        return message

if __name__ == "__main__":
    get_weather('kyiv',open_weather_token)