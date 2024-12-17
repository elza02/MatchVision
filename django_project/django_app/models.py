# models.py
from django.db import models

class Team(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    competition_name = models.CharField(max_length=100)
    venue = models.CharField(max_length=100, null=True)
    website = models.URLField(max_length=200, null=True)
    founded = models.IntegerField(null=True)
    club_colors = models.CharField(max_length=100, null=True)
    crest = models.URLField(max_length=200, null=True)
   
    class Meta:
        db_table = 'teams'

    def __str__(self):
        return self.name

class Competition(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, null=True, default='')
    area = models.CharField(max_length=100, null=True, default='')
    code = models.CharField(max_length=20, null=True, default='')
    type = models.CharField(max_length=20, null=True, default='LEAGUE')
    emblem = models.CharField(max_length=200, null=True, default='')

    class Meta:
        db_table = 'competitions'

    def __str__(self):
        return self.name

class Match(models.Model):
    id = models.IntegerField(primary_key=True)
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, null=True)
    season = models.CharField(max_length=20, null=True, default='')
    home_team = models.ForeignKey(Team, related_name='home_matches', on_delete=models.CASCADE, null=True)
    away_team = models.ForeignKey(Team, related_name='away_matches', on_delete=models.CASCADE, null=True)
    match_date = models.DateTimeField(null=True)
    status = models.CharField(max_length=20, null=True, default='')
    stage = models.CharField(max_length=50, null=True, default='')
    home_team_score = models.IntegerField(null=True, default=0)
    away_team_score = models.IntegerField(null=True, default=0)
    referee = models.CharField(max_length=100, null=True, default='')
    
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
    name = models.CharField(max_length=100, null=True, default='')
    position = models.CharField(max_length=50, null=True, default='')
    nationality = models.CharField(max_length=100, null=True, default='')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True)
    goals = models.IntegerField(null=True, default=0)
    assists = models.IntegerField(null=True, default=0)
    minutes_played = models.IntegerField(null=True, default=0)
    match = models.ForeignKey(Match, on_delete=models.CASCADE, null=True)

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
    id = models.AutoField(primary_key=True)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    home_win_odds = models.FloatField()
    draw_odds = models.FloatField()
    away_win_odds = models.FloatField()
    timestamp = models.DateTimeField()  # Changed to store API timestamp
       
    class Meta:
        db_table = 'betting_odds'
        indexes = [
            models.Index(fields=['match', 'timestamp']),  # Index for efficient querying
        ]

    def __str__(self):
        return f"Odds for {self.match} at {self.timestamp}"

class TopScorer(models.Model):
    player_id = models.IntegerField(primary_key=True)
    player_name = models.CharField(max_length=100, null=True, default='')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True)
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, null=True)
    season = models.CharField(max_length=20, null=True, default='')
    goals = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)
    played_matches = models.IntegerField(default=0)
    penalties = models.IntegerField(default=0)

    class Meta:
        db_table = 'top_scorers'
        unique_together = ('player_id', 'competition', 'season')

    def __str__(self):
        return f"{self.player_name} - {self.goals} goals ({self.competition}, {self.season})"

class TwitterFeed(models.Model):
    tweet_id = models.CharField(max_length=100, primary_key=True)
    content = models.TextField()
    author = models.CharField(max_length=100)
    author_username = models.CharField(max_length=100)
    author_profile_image = models.URLField(max_length=500, null=True)
    created_at = models.DateTimeField()
    likes_count = models.IntegerField(default=0)
    retweets_count = models.IntegerField(default=0)
    media_urls = models.JSONField(null=True)  # Store URLs of images/videos
    related_team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True)
    related_competition = models.ForeignKey(Competition, on_delete=models.SET_NULL, null=True)
    category = models.CharField(max_length=50, choices=[
        ('NEWS', 'News'),
        ('TRANSFER', 'Transfer'),
        ('MATCH', 'Match'),
        ('HIGHLIGHT', 'Highlight'),
        ('OTHER', 'Other')
    ], default='OTHER')

    class Meta:
        db_table = 'twitter_feeds'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.author} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"

class Goal(models.Model):
    id = models.AutoField(primary_key=True)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    scorer = models.ForeignKey(Player, related_name='goals_scored', on_delete=models.CASCADE)
    assistant = models.ForeignKey(Player, related_name='goals_assisted', on_delete=models.CASCADE, null=True, blank=True)
    minute = models.IntegerField()
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=[
        ('REGULAR', 'Regular'),
        ('PENALTY', 'Penalty'),
        ('OWN_GOAL', 'Own Goal'),
        ('FREE_KICK', 'Free Kick')
    ], default='REGULAR')

    class Meta:
        db_table = 'goals'
        ordering = ['match', 'minute']

    def __str__(self):
        return f"{self.scorer} ({self.minute}') - {self.match}"