class Game:
    def __init__(self, date, home_team, away_team, home_team_odds, away_team_odds):
        self.date = date
        self.home_team = home_team
        self.away_team = away_team
        self.home_team_odds = home_team_odds
        self.away_team_odds = away_team_odds

    def __str__(self):
        return (f"Date: {self.date}\n"
                f"Home Team: {self.home_team}\n"
                f"Away Team: {self.away_team}\n"
                f"Home Team Odds: {self.home_team_odds}\n"
                f"Away Team Odds: {self.away_team_odds}")
