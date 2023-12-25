import pytz
import requests
import os
from dotenv import load_dotenv
from datetime import datetime, date, timedelta

load_dotenv()
url = "https://odds.p.rapidapi.com/v4/sports/basketball_nba/scores"
API_KEY = os.getenv("RESULTS_API_KEY")
querystring = {"daysFrom": "2"}
headers = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "odds.p.rapidapi.com"
}


def get_game_results():
    response = requests.get(url, headers=headers, params=querystring)
    return response.json()


def filter_results_data(games, game_date):
    results = []
    for game in games:
        # print(game)
        if convert_utc_to_est(game['commence_time']) == game_date:
            game['commence_time'] = convert_utc_to_est(game['commence_time']).strftime('%Y-%m-%d')
            results.append(game)
    return results


def convert_utc_to_est(utc_datetime_str):
    utc_datetime = datetime.strptime(utc_datetime_str, '%Y-%m-%dT%H:%M:%SZ')
    utc_timezone = pytz.timezone('UTC')
    utc_datetime = utc_timezone.localize(utc_datetime)
    est_timezone = pytz.timezone('America/New_York')
    est_datetime = utc_datetime.astimezone(est_timezone)
    est_date = est_datetime.date()
    return est_date


# filter_results_data(get_game_results(), date.today() - timedelta(days=2))
