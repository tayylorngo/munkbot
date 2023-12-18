from datetime import datetime

import requests
import os
from dotenv import load_dotenv

from game import Game

load_dotenv()
API_KEY = os.getenv("API_KEY")
URL = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?regions=us&oddsFormat=decimal&apiKey=" + API_KEY


def get_data():
    sports_response = requests.get(URL)
    if sports_response.status_code != 200:
        print(f'Failed to get sports: status_code {sports_response.status_code}, response body {sports_response.text}')
    else:
        return sports_response.json()


def is_today(game):
    game_date = datetime.strptime(game['commence_time'], "%Y-%m-%dT%H:%M:%SZ")
    return game_date.day == datetime.now().day

def is_fanduel(bookmakers):
    pass


def filter_data(data):
    filter(is_today, data)
    results =[]
    for game in data:
        print(game['bookmakers'])
        date = datetime.strptime(game['commence_time'], "%Y-%m-%dT%H:%M:%SZ")
        home_team = game['home_team']
        away_team = game['away_team']
        # results.append(Game())
    return data


print(filter_data(get_data()))