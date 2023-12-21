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