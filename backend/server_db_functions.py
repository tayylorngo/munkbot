import datetime
import math


def init_server_data(db):
    db.games.insert_one(
        {
            "name": "red_army",
            "wins": 0,
            "losses": 0,
            "ties": 0,
            "favorite_team": "",
            "least_favorite_team": "",
            "voted_teams": {}
        }
    )


def get_server_data(db):
    return db.games.find_one(
        {
            "name": "red_army"
        }
    )


def calculate_leaderboard_ranking(user):
    wins = user['betting_stats']['wins']
    total_games_played = user['betting_stats']['wins'] + user['betting_stats']['losses']
    win_percent = wins / total_games_played if total_games_played > 0 else 0
    weight_factor = math.sqrt(total_games_played)
    return win_percent * weight_factor


def set_leaderboard(user_db, server_db):
    server_db.leaderboard.insert_one({
        "date": str(datetime.datetime.now().date()),
        "leaderboard": sorted(user_db.users.find({}), key=calculate_leaderboard_ranking, reverse=True)
    })


def get_leaderboard_by_date(server_db, date):
    return server_db.leaderboard.find_one({"date": date})


def get_leaderboard_today(server_db):
    return server_db.leaderboard.find_one({"date": str(datetime.datetime.now().date())})
