class Game:
    def __init__(self, date, home_team, away_team, home_team_odds, away_team_odds):
        self.date = date
        self.home_team = home_team
        self.away_team = away_team
        self.home_team_odds = home_team_odds
        self.away_team_odds = away_team_odds

    def __str__(self):
        return f"{self.away_team} ({self.away_team_odds}) @ {self.home_team} ({self.home_team_odds})"
