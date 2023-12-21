from nba_logos import get_key


def add_new_user(db, game, user, reaction):
    db.users.create_one(
        {
            "user_id": user.id,
            "username": user.name,
            "games_voted_on": [].append(game["_id"]),
            "teams_voted_on": {
                get_key(str(reaction)): 1
            },
            "betting_stats": {
                "average_betting_odds": 0,
                "win_percent": 0,
                "lose_percent": 0,
                "favorite_team": "",
                "least_favorite_team": "",
            }
        }
    )


def get_user(db, user_id):
    key = {"user_id": user_id}
    user = db.users.findOne(key)
    return user


def update_user_on_vote(db, user, game, reaction):
    new_games_voted_on_list = user["games_voted_on"]
    new_games_voted_on_list.append(game["_id"])
    new_teams_voted_on = user["teams_voted_on"]
    count = 1
    if get_key(str(reaction)) in new_teams_voted_on:
        count = new_teams_voted_on['teams_voted_on'][get_key(reaction)] + 1
    new_teams_voted_on.update(
        {
            get_key(str(reaction)): count
        }
    )
    if game.home_team == get_key(str(reaction)):
        new_betting_odds = ((user["betting_stats"]["average_betting_odds"] * len(user["games_voted_on"])
                            + game.home_team_odds) / (len(user["games_voted_on"]) + 1))
    else:
        new_betting_odds = ((user["betting_stats"]["average_betting_odds"] * len(user["games_voted_on"])
                             + game.away_team_odds) / (len(user["games_voted_on"]) + 1))
    new_betting_stats = user['betting_stats']
    new_betting_stats.update(
        {
            "average_betting_odds": new_betting_odds
        }
    )
    user_filter = {'user_id': user.id}
    new_values = {"$set": {
        "games_voted_on": new_games_voted_on_list,
        "teams_voted_on": new_teams_voted_on,
        "betting_stats": new_betting_stats
    }}
    db.users.update_one(user_filter, new_values)