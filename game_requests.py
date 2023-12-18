import requests
import os
from dotenv import load_dotenv

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
    pass
