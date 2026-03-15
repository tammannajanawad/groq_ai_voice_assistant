import datetime
import requests


def get_time():
    return str(datetime.datetime.now())


def get_weather(city):

    url = f"https://wttr.in/{city}?format=3"
    return requests.get(url).text


TOOLS = {
    "get_time": get_time,
    "get_weather": get_weather
}