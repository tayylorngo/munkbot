from datetime import datetime

import requests
import os
from dotenv import load_dotenv

from game import Game
from results_request import convert_utc_to_est

load_dotenv()
API_KEY = os.getenv("API_KEY")
URL = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?regions=us&oddsFormat=decimal&apiKey=" + API_KEY


def get_data():
    sports_response = requests.get(URL)
    if sports_response.status_code != 200:
        print(f'Failed to get sports: status_code {sports_response.status_code}, response body {sports_response.text}')
    else:
        return sports_response.json()


def filter_data(data):
    results = []
    for game in data:
        game_date = convert_utc_to_est(game['commence_time'])

        if game_date != datetime.today().date():
            continue
        date = datetime.strptime(game['commence_time'], "%Y-%m-%dT%H:%M:%SZ")
        date = date.replace(day=datetime.today().day, hour=0, minute=0, second=0, microsecond=0)
        home_team = game['home_team']
        away_team = game['away_team']
        for bookmaker in game['bookmakers']:
            if bookmaker['key'] == 'fanduel':
                odds = bookmaker['markets'][0]['outcomes']
                if odds[0]['name'] == home_team:
                    home_team_odds = odds[0]['price']
                    away_team_odds = odds[1]['price']
                else:
                    home_team_odds = odds[1]['price']
                    away_team_odds = odds[0]['price']
                results.append(Game(date, home_team, away_team, home_team_odds, away_team_odds))
                break
    return results


# game_list = filter_data(get_data())
# for game in game_list:
#     print(game)
