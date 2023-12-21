from datetime import datetime

from nba_logos import get_key


def add_new_game(db, game):
    db.games.insert_one(
        {
            "date": game.date,
            "away_team": game.away_team,
            "home_team": game.home_team,
            "away_team_odds": game.away_team_odds,
            "home_team_odds": game.home_team_odds,
            "winning_team": "",
            "losing_team": "",
            "majority_team": "",
            "away_team_voters": [],
            "home_team_voters": []
        }
    )


def add_new_user(db, game, user, reaction):
    db.users.create_one(
        {
            "user_id": user.id,
            "username": user.name,
            "games_voted_on": [].append(game["_id"]),
            "teams_voted_on": {
                get_key(str(reaction)): 1
            },
            "win_percent": 0,
            "lose_percent": 0,
            "favorite_team": "",
            "least_favorite_team": "",
        }
    )


def get_today_games(db):
    key = {"date": datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)}
    today_games = db.games.find(key)
    for game in today_games:
        print(game)
    return today_games


def get_user(db, user_id):
    key = {"user_id": user_id}
    user = db.users.find(key)
    return user
