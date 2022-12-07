import requests
import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla Inc"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

STOCK_API_KEY = os.environ["STOCK_API_KEY"]
NEWS_API_KEY = os.environ["NEWS_API_KEY"]
TWILIO_SID = os.environ["TWILIO_SID"]
AUTH_TOKEN = os.environ["AUTH_TOKEN"]


stock_params = {
    "function": "TIME_SERIES_INTRADAY",
    "symbol": STOCK_NAME,
    "interval": "30min",
    "apikey": STOCK_API_KEY,

}

news_params = {
    "apiKey": NEWS_API_KEY,
    "q": STOCK_NAME,
    "searchIn": "title",
    "sortBy": "publishedAt",
}

response = requests.get(STOCK_ENDPOINT, params=stock_params)
response.raise_for_status()
stock_data = response.json()["Time Series (30min)"]
data_list = [value for (key, value) in stock_data.items()]

yesterday_data = data_list[8]
yesterday_closing_price = yesterday_data["4. close"]

day_before_yesterday_close = data_list[40]["4. close"]

difference = float(yesterday_closing_price) - float(day_before_yesterday_close)
up_down = None
if difference > 0:
    up_down = "🔺"
else:
    up_down = "🔻"

percent_diff = round(100 * (difference / (float(yesterday_closing_price))))

if abs(percent_diff) > 5:
    news_response = requests.get(NEWS_ENDPOINT, news_params)
    news_response.raise_for_status()
    articles = news_response.json()["articles"]
    three_articles = articles[:3]

    formatted_articles = [f"{STOCK_NAME}: {up_down}{percent_diff}%\nHeadline: {article['title']}. \nBrief: " \
                          f"{article['description']}" for article in three_articles]
    client = Client(TWILIO_SID, AUTH_TOKEN)
    for article in formatted_articles:
        message = client.messages.create(
            body=article,
            from_='+15044144801',
            to='+12026707145'
        )