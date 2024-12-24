# models.py
from django.db import models

class Team(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    short_name = models.CharField(max_length=50, null=True, blank=True)
    tla = models.CharField(max_length=10, null=True, blank=True)
    crest = models.URLField(max_length=200, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    website = models.URLField(max_length=200, null=True, blank=True)
    founded = models.IntegerField(null=True, blank=True)
    club_colors = models.CharField(max_length=100, null=True, blank=True)
    venue = models.CharField(max_length=100, null=True, blank=True)
    area = models.ForeignKey('Area', models.SET_NULL, null=True, blank=True)
    coach = models.ForeignKey('Coach', models.SET_NULL, null=True, blank=True)
    season = models.CharField(max_length=20, null=True, blank=True)
     
    class Meta:
        db_table = 'teams'

    def __str__(self):
        return self.name or self.short_name or f"Team {self.id}"

    @property
    def display_name(self):
        return self.name or self.short_name or f"Team {self.id}"
    
class TeamCompetition(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True)
    competition = models.ForeignKey('Competition', on_delete=models.CASCADE, null=True)
    season = models.CharField(max_length=20, null=True)
    
    class Meta:
        db_table = 'team_competitions'
        unique_together = ('team', 'competition', 'season')

    def __str__(self):
        return f"{self.team} - {self.competition} ({self.season})"


class Coach(models.Model):
    first_name = models.CharField(max_length=50, null=True)
    last_name = models.CharField(max_length=50, null=True)
    name = models.CharField(max_length=100, null=True)
    date_of_birth = models.DateField(null=True)
    nationality = models.CharField(max_length=100, null=True)
    contract_start_date = models.DateField(null=True)
    contract_end_date = models.DateField(null=True)
    
    class Meta:
        db_table = 'coaches'


class Player(models.Model):
    name = models.CharField(max_length=100, null=True)
    section = models.CharField(max_length=50, null=True)
    date_of_birth = models.DateField(null=True)
    nationality = models.CharField(max_length=100, null=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='players', null=True)
    
    class Meta:
        db_table = 'players'
    
    
class Area(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    flag = models.URLField(max_length=200, null=True)

    class Meta:
        db_table = 'areas'

    def __str__(self):
        return self.name


class Competition(models.Model):
    name = models.CharField(max_length=100, null=True, default='')
    code = models.CharField(max_length=20, null=True, default='')
    type = models.CharField(max_length=20, null=True, default='LEAGUE')
    emblem = models.CharField(max_length=200, null=True, default='')
    area = models.ForeignKey(Area, on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = 'competitions'

    def __str__(self):
        return self.name


class Match(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, null=True)
    match_date = models.DateField(null=True)
    status = models.CharField(max_length=20, null=True, default='')
    stage = models.CharField(max_length=50, null=True, default='')
    home_team = models.ForeignKey(Team, related_name='home_matches', on_delete=models.CASCADE, null=True)
    away_team = models.ForeignKey(Team, related_name='away_matches', on_delete=models.CASCADE, null=True)
    home_team_score = models.IntegerField(null=True, default=0)
    away_team_score = models.IntegerField(null=True, default=0)
    season = models.CharField(max_length=20, null=True, default='')
    area = models.ForeignKey(Area, on_delete=models.CASCADE, null=True)
    
    class Meta:
        db_table = 'matches'

    def __str__(self):
        return f"{self.home_team} vs {self.away_team}"
    
    
class TopScorer(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, null=True)
    player = models.ForeignKey(Player, on_delete=models.CASCADE, null=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True)
    played_matches = models.IntegerField(default=0, null=True)
    goals = models.IntegerField(default=0, null=True)
    assists = models.IntegerField(default=0, null=True)
    penalties = models.IntegerField(default=0, null=True)
    season = models.CharField(max_length=20, null=True, default='')

    class Meta:
        db_table = 'top_scorers'
        unique_together = ('player_id', 'competition', 'season')

    def __str__(self):
        return f"{self.player_name} - {self.goals} goals ({self.competition}, {self.season})"


class Standing(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, null=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, null=True)
    position = models.IntegerField(default=0)
    played_games = models.IntegerField(default=0)
    form = models.CharField(max_length=10, null=True, default='')
    won = models.IntegerField(default=0)
    draw = models.IntegerField(default=0)
    lost = models.IntegerField(default=0)
    points = models.IntegerField(default=0)
    goals_for = models.IntegerField(default=0)
    goals_against = models.IntegerField(default=0)
    goal_difference = models.IntegerField(default=0)
    season = models.CharField(max_length=20, null=True, default='')

    class Meta:
        db_table = 'standings'
        unique_together = ('team', 'competition', 'season')

    def __str__(self):
        return f"{self.team} - {self.points} points ({self.competition}, {self.season})"
