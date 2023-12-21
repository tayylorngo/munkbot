from nba_logos import get_key


def add_new_user(db, game, user, reaction, voted_team):
    games_list = [game["_id"]]
    if game["home_team"] == voted_team:
        odds = game["home_team_odds"]
    else:
        odds = game["away_team_odds"]
    db.users.insert_one(
        {
            "user_id": user.id,
            "username": user.name,
            "games_voted_on": games_list,
            "teams_voted_on": {
                get_key(str(reaction)): 1
            },
            "betting_stats": {
                "average_betting_odds": odds,
                "win_percent": 0,
                "lose_percent": 0,
                "favorite_team": voted_team,
                "least_favorite_team": "",
            }
        }
    )


def get_user(db, user_id):
    key = {"user_id": user_id}
    user = db.users.find_one(key)
    return user


def update_user_on_vote(db, user, game, reaction, voted_team):
    new_games_voted_on_list = user["games_voted_on"]
    new_games_voted_on_list.append(game["_id"])
    new_teams_voted_on = user["teams_voted_on"]
    count = 1
    if voted_team in new_teams_voted_on:
        count = new_teams_voted_on['teams_voted_on'][get_key(reaction)] + 1
    new_teams_voted_on.update(
        {
            voted_team: count
        }
    )
    if game["home_team"] == voted_team:
        new_betting_odds = ((user["betting_stats"]["average_betting_odds"] * (len(user["games_voted_on"]) - 1)
                             + game["home_team_odds"]) / (len(user["games_voted_on"])))
    else:
        new_betting_odds = ((user["betting_stats"]["average_betting_odds"] * (len(user["games_voted_on"]) - 1)
                             + game["away_team_odds"]) / (len(user["games_voted_on"])))
    new_betting_stats = user['betting_stats']
    new_betting_stats.update(
        {
            "average_betting_odds": new_betting_odds
        }
    )
    user_filter = {'user_id': user["user_id"]}
    new_values = {"$set": {
        "games_voted_on": new_games_voted_on_list,
        "teams_voted_on": new_teams_voted_on,
        "betting_stats": new_betting_stats
    }}
    db.users.update_one(user_filter, new_values)


def update_user_on_vote_remove(db, user, game, reaction, voted_team):
    new_games_voted_on_list = user["games_voted_on"]
    new_games_voted_on_list.remove(game["_id"])
    new_teams_voted_on = user["teams_voted_on"]
    count = new_teams_voted_on[get_key(reaction)] - 1
    new_teams_voted_on.update(
        {
            voted_team: count
        }
    )
    if len(user["games_voted_on"]) == 0:
        new_betting_odds = 0
    elif game["home_team"] == voted_team:
        new_betting_odds = ((user["betting_stats"]["average_betting_odds"] * len(user["games_voted_on"])
                             - game["home_team_odds"]) / (len(user["games_voted_on"])))
    else:
        new_betting_odds = ((user["betting_stats"]["average_betting_odds"] * len(user["games_voted_on"])
                             - game["away_team_odds"]) / (len(user["games_voted_on"])))
    new_betting_stats = user['betting_stats']
    new_betting_stats.update(
        {
            "average_betting_odds": new_betting_odds
        }
    )
    user_filter = {'user_id': user["user_id"]}
    new_values = {"$set": {
        "games_voted_on": new_games_voted_on_list,
        "teams_voted_on": new_teams_voted_on,
        "betting_stats": new_betting_stats
    }}
    db.users.update_one(user_filter, new_values)
