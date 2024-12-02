# models.py
from django.db import models

class Team(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    venue = models.CharField(max_length=100)

    class Meta:
        db_table = 'teams'

    def __str__(self):
        return self.name

class Competition(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    area = models.CharField(max_length=100)

    class Meta:
        db_table = 'competitions'

    def __str__(self):
        return self.name

class Match(models.Model):
    id = models.IntegerField(primary_key=True)
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    season = models.CharField(max_length=20, default='2023/24')
    home_team = models.ForeignKey(Team, related_name='home_matches', on_delete=models.CASCADE)
    away_team = models.ForeignKey(Team, related_name='away_matches', on_delete=models.CASCADE)
    match_date = models.DateTimeField()
    status = models.CharField(max_length=20)
    home_team_score = models.IntegerField(default=0, null=True)
    away_team_score = models.IntegerField(default=0, null=True)
    referee = models.CharField(max_length=100, null=True)
    
    class Meta:
        db_table = 'matches'

    def __str__(self):
        return f"{self.home_team} vs {self.away_team}"

class Player(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=50)
    nationality = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='players')
    shirt_number = models.IntegerField(null=True)
    age = models.IntegerField(null=True)
    market_value = models.DecimalField(max_digits=12, decimal_places=2, null=True)

    class Meta:
        db_table = 'players'

    def __str__(self):
        return f"{self.name} ({self.team})"

class PlayerStats(models.Model):
    player_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=50)
    goals = models.IntegerField(default=0, null=False)
    assists = models.IntegerField(default=0, null=False)
    minutes_played = models.IntegerField(default=0, null=False)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)

    class Meta:
        db_table = 'player_stats'

    def __str__(self):
        return f"{self.name} - {self.team}"

class MatchPrediction(models.Model):
    match = models.OneToOneField(Match, primary_key=True, on_delete=models.CASCADE)
    home_team_win_prob = models.FloatField(default=0.0, null=False)
    draw_prob = models.FloatField(default=0.0, null=False)
    away_team_win_prob = models.FloatField(default=0.0, null=False)
    predicted_score = models.CharField(max_length=20)
    
    class Meta:
        db_table = 'match_predictions'

    def __str__(self):
        return f"Prediction for {self.match}"

class TeamFormation(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    formation = models.CharField(max_length=20)
    players = models.JSONField()
    
    class Meta:
        db_table = 'team_formations'
        unique_together = ('match', 'team')
    
    def __str__(self):
        return f"{self.team} formation in {self.match}"

class BettingOdds(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    home_win_odds = models.FloatField(default=0.0, null=False)
    draw_odds = models.FloatField(default=0.0, null=False)
    away_win_odds = models.FloatField(default=0.0, null=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'betting_odds'

    def __str__(self):
        return f"Odds for {self.match}"

class TopScorer(models.Model):
    player_id = models.IntegerField(primary_key=True)
    player_name = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    season = models.CharField(max_length=20)
    goals = models.IntegerField(default=0, null=False)
    assists = models.IntegerField(default=0, null=False)
    played_matches = models.IntegerField(default=0, null=False)
    
    class Meta:
        db_table = 'top_scorers'

    def __str__(self):
        return f"{self.player_name} - {self.goals} goals"