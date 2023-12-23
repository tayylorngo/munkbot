from datetime import datetime, timedelta


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
    return today_games


def get_yesterday_games(db):
    yesterday_date = datetime.today() - timedelta(days=1)
    key = {"date": yesterday_date.replace(hour=0, minute=0, second=0, microsecond=0)}
    yesterday_games = db.games.find(key)
    return yesterday_games


def game_add_message_id(db, game, message_id):
    game_filter = {"_id": game["_id"]}
    new_values = {"$set": {
        "message_id": message_id
    }}
    db.games.update_one(game_filter, new_values)


def update_game_votes(db, user, voted_team, message, add):
    game = get_game(db, message.id)
    home_team_voters = game["home_team_voters"]
    away_team_voters = game["away_team_voters"]
    if add:
        if voted_team == game["home_team"]:
            home_team_voters.append(user["user_id"])
        else:
            away_team_voters.append(user["user_id"])
    else:
        if voted_team == game["home_team"]:
            home_team_voters.remove(user["user_id"])
        else:
            away_team_voters.remove(user["user_id"])
    if len(home_team_voters) > len(away_team_voters):
        majority_team = game["home_team"]
    elif len(home_team_voters) < len(away_team_voters):
        majority_team = game["away_team"]
    else:
        majority_team = "tie"

    game_filter = {'message_id': message.id}
    new_values = {"$set": {
        "home_team_voters": home_team_voters,
        "away_team_voters": away_team_voters,
        "majority_team": majority_team
    }}
    db.games.update_one(game_filter, new_values)


def update_game_results(db, game):
    game_date = datetime.strptime(game["commence_time"], '%Y-%m-%d').date()
    home_team_score = game['scores'][0]['score']
    away_team_score = game['scores'][1]['score']
    if home_team_score > away_team_score:
        winning_team = game['scores'][0]['name']
    else:
        winning_team = game['scores'][1]['name']
    new_values = {"$set": {
        "winning_team": winning_team
    }}
    game_filter = {
        "date": game_date,
        "home_team": game['home_team'],
        "away_team": game['away_team']
    }
    db.games.update_one(game_filter, new_values)


def get_game(db, message_id):
    key = {"message_id": message_id}
    return db.games.find_one(key)
