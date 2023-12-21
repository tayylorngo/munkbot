from datetime import datetime


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
            "home_team_voters": [],
            "message_id": ""
        }
    )


def get_today_games(db):
    key = {"date": datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)}
    today_games = db.games.find(key)
    # for game in today_games:
    #     print(game)
    return today_games


def game_add_message_id(db, game, message_id):
    game_filter = {"_id": game["_id"]}
    new_values = {"$set": {
        "message_id": message_id
    }}
    db.games.update_one(game_filter, new_values)


