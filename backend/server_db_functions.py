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
