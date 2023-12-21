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
                "betting_odds": [],
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