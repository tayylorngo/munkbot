from backend.game_db_functions import get_game_by_id
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


def get_all_users(db):
    return db.users.find()


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
    (least_favorite_team
     , least_favorite_team_votes
     , favorite_team
     , favorite_team_votes) = find_favorite_team(new_teams_voted_on)
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
    (least_favorite_team
     , least_favorite_team_votes
     , favorite_team
     , favorite_team_votes) = find_favorite_team(new_teams_voted_on)
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

        user_betting_stats["wins"] = user_betting_stats["wins"] + 1
        user_betting_stats["win_percent"] = (user_betting_stats['wins']
                                             / (user_betting_stats['wins'] + user_betting_stats['losses']))

        user_betting_stats["lose_percent"] = (user_betting_stats['losses']
                                              / (user_betting_stats['wins'] + user_betting_stats['losses']))

        user_filter = {'user_id': user_id}
        new_values = {"$set": {
            "betting_stats": user_betting_stats
        }}
        db.users.update_one(user_filter, new_values)
    for user_id in game[loser]:
        user = get_user(db, user_id)
        user_betting_stats = user['betting_stats']
        user_betting_stats["losses"] = user_betting_stats["losses"] + 1
        user_betting_stats["win_percent"] = (user_betting_stats['wins']
                                             / (user_betting_stats['wins'] + user_betting_stats['losses']))
        user_betting_stats["lose_percent"] = (user_betting_stats['losses']
                                              / (user_betting_stats['wins'] + user_betting_stats['losses']))
        user_filter = {'user_id': user_id}
        new_values = {"$set": {
            "betting_stats": user_betting_stats
        }}
        db.users.update_one(user_filter, new_values)


def find_favorite_team(teams_voted_on):
    if not teams_voted_on:
        return None, None, None, None

    # Find the key-value pairs with the smallest and largest values in the dictionary
    least_favorite_team, least_favorite_team_votes = min(teams_voted_on.items(), key=lambda x: x[1])
    favorite_team, favorite_team_votes = max(teams_voted_on.items(), key=lambda x: x[1])

    return least_favorite_team, least_favorite_team_votes, favorite_team, favorite_team_votes


def update_user_manual(db, game_db, username):
    for user in db.users.find({"username": username}):
        user_games_voted_on = user["games_voted_on"]
        updated_betting_stats = {
            "wins": 0,
            "losses": 0,
            "average_betting_odds": 0,
            "win_percent": 0,
            "lose_percent": 0,
            "favorite_team": "",
            "least_favorite_team": "",
        }
        updated_teams_voted_on = {}
        for game_id in user_games_voted_on:
            game = get_game_by_id(game_db, game_id)
            selected_team = ""
            if user["user_id"] in game["away_team_voters"]:
                selected_team = "away_team"
            elif user["user_id"] in game["home_team_voters"]:
                selected_team = "home_team"
            if game['winning_team'] == "":
                continue
            elif game['winning_team'] == game[selected_team]:
                updated_betting_stats["wins"] += 1
                updated_betting_stats["win_percent"] = (updated_betting_stats["wins"]
                                                        / (updated_betting_stats["wins"]
                                                           + updated_betting_stats["losses"]))
            else:
                updated_betting_stats["losses"] += 1
            updated_betting_stats["lose_percent"] = 1 - updated_betting_stats["win_percent"]
            if updated_betting_stats["average_betting_odds"] == 0:
                updated_betting_stats["average_betting_odds"] = game[selected_team + "_odds"]
            else:
                updated_betting_stats["average_betting_odds"] = ((updated_betting_stats["average_betting_odds"]
                                                                  * (updated_betting_stats["wins"]
                                                                     + updated_betting_stats["losses"] - 1))
                                                                 + game[selected_team + "_odds"])
                updated_betting_stats["average_betting_odds"] = (updated_betting_stats["average_betting_odds"]
                                                                 / (updated_betting_stats["wins"]
                                                                    + updated_betting_stats["losses"]))
            if game[selected_team] not in updated_teams_voted_on:
                updated_teams_voted_on[game[selected_team]] = 1
            else:
                updated_teams_voted_on[game[selected_team]] += 1
            (least_favorite_team
             , least_favorite_team_votes
             , favorite_team
             , favorite_team_votes) = find_favorite_team(updated_teams_voted_on)
            updated_betting_stats["favorite_team"] = favorite_team
            updated_betting_stats["least_favorite_team"] = least_favorite_team
            db.users.update_one({"user_id": user["user_id"]},
                                {"$set": {
                                    "teams_voted_on": updated_teams_voted_on,
                                    "betting_stats": updated_betting_stats
                                }})
    print("DONE")
