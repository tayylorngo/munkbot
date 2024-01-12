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
            "display_name": user.display_name,
            "display_avatar": user.display_avatar,
            "games_voted_on": games_list,
            "teams_voted_on": {
                get_key(str(reaction)): 1
            },
            "betting_stats": {
                "wins": 0,
                "losses": 0,
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


def get_user_by_name(db, username):
    key = {"display_name": username}
    user = db.users.find_one(key)
    return user


def update_user_on_vote(db, user, game, voted_team):
    new_games_voted_on_list = user["games_voted_on"]
    new_games_voted_on_list.append(game["_id"])
    new_teams_voted_on = user["teams_voted_on"]
    count = 1
    if voted_team in new_teams_voted_on:
        count = new_teams_voted_on[voted_team] + 1
    new_teams_voted_on.update(
        {
            voted_team: count
        }
    )
    curr = 0
    curr2 = max(new_teams_voted_on.values())
    favorite_team = ""
    least_favorite_team = ""
    for key in new_teams_voted_on.keys():
        if new_teams_voted_on[key] >= curr:
            curr = new_teams_voted_on[key]
            favorite_team = key
        if new_teams_voted_on[key] <= curr2:
            curr2 = new_teams_voted_on[key]
            least_favorite_team = key
    if game["home_team"] == voted_team:
        new_betting_odds = ((user["betting_stats"]["average_betting_odds"] * (len(user["games_voted_on"]) - 1)
                             + game["home_team_odds"]) / (len(user["games_voted_on"])))
    else:
        new_betting_odds = ((user["betting_stats"]["average_betting_odds"] * (len(user["games_voted_on"]) - 1)
                             + game["away_team_odds"]) / (len(user["games_voted_on"])))
    update_user_betting_stats(db, user, new_betting_odds
                              , user['betting_stats'], new_games_voted_on_list,
                              new_teams_voted_on, favorite_team, least_favorite_team)


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
    curr = 0
    curr2 = max(new_teams_voted_on.values(), default=0)
    favorite_team = ""
    least_favorite_team = ""
    for key in new_teams_voted_on.keys():
        if new_teams_voted_on[key] >= curr:
            curr = new_teams_voted_on[key]
            favorite_team = key
        if new_teams_voted_on[key] <= curr2:
            curr2 = new_teams_voted_on[key]
            least_favorite_team = key

    if len(user["games_voted_on"]) == 0:
        new_betting_odds = 0
    elif game["home_team"] == voted_team:
        new_betting_odds = ((user["betting_stats"]["average_betting_odds"] * (len(user["games_voted_on"]) + 1)
                             - game["home_team_odds"]) / (len(user["games_voted_on"])))
    else:
        new_betting_odds = ((user["betting_stats"]["average_betting_odds"] * (len(user["games_voted_on"]) + 1)
                             - game["away_team_odds"]) / (len(user["games_voted_on"])))

    update_user_betting_stats(db, user, new_betting_odds
                              , user['betting_stats'], new_games_voted_on_list,
                              new_teams_voted_on, favorite_team, least_favorite_team)


def update_user_betting_stats(db, user, new_betting_odds,
                              new_betting_stats, new_games_voted_on_list,
                              new_teams_voted_on, favorite_team, least_favorite_team):
    new_betting_stats.update(
        {
            "average_betting_odds": new_betting_odds,
            "favorite_team": favorite_team,
            "least_favorite_team": least_favorite_team
        }
    )
    user_filter = {'user_id': user["user_id"]}
    new_values = {"$set": {
        "games_voted_on": new_games_voted_on_list,
        "teams_voted_on": new_teams_voted_on,
        "betting_stats": new_betting_stats
    }}
    db.users.update_one(user_filter, new_values)


def update_user_results(db, game):
    if game['home_team'] == game['winning_team']:
        winner = 'home_team_voters'
        loser = 'away_team_voters'
    else:
        winner = 'away_team_voters'
        loser = 'home_team_voters'

    for user_id in game[winner]:
        user = get_user(db, user_id)
        user_betting_stats = user['betting_stats']
        user_betting_stats.update({
            "wins": user_betting_stats['wins'] + 1,
            "win_percent": (user_betting_stats['wins'] + 1) / (user_betting_stats['wins']
                                                               + user_betting_stats['losses'] + 1),
            "lose_percent": user_betting_stats['losses'] / (user_betting_stats['wins']
                                                            + user_betting_stats['losses'] + 1),
        })
        user_filter = {'user_id': user_id}
        new_values = {"$set": {
            "betting_stats": user_betting_stats
        }}
        db.users.update_one(user_filter, new_values)
    for user_id in game[loser]:
        user = get_user(db, user_id)
        user_betting_stats = user['betting_stats']
        user_betting_stats.update({
            "losses": user_betting_stats['losses'] + 1,
            "win_percent": user_betting_stats['wins'] / (user_betting_stats['wins']
                                                         + user_betting_stats['losses'] + 1),
            "lose_percent": (user_betting_stats['losses'] + 1) / (user_betting_stats['wins']
                                                                  + user_betting_stats['losses'] + 1),
        })
