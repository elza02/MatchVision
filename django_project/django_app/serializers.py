from rest_framework import serializers
from .models import (
    Team, Competition, Match, PlayerStats, Player, 
    MatchPrediction, TeamFormation, BettingOdds, TopScorer
)

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = [
            'id', 'name', 'competition_name', 'venue', 
            'website', 'founded', 'club_colors', 'crest'
        ]


class CompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = '__all__'


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['id', 'name']  # Add other team fields if needed

class MatchSerializer(serializers.ModelSerializer):
    home_team_details = TeamSerializer(source='home_team', read_only=True)
    away_team_details = TeamSerializer(source='away_team', read_only=True)

    class Meta:
        model = Match
        fields = [
            'id', 'season', 'match_date', 'status', 'stage',
            'home_team_score', 'away_team_score', 'referee', 'competition',
            'home_team_details', 'away_team_details'  # Include team details
        ]






class PlayerStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerStats
        fields = '__all__'

class MatchPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchPrediction
        fields = '__all__'

class TeamFormationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamFormation
        fields = '__all__'

class BettingOddsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BettingOdds
        fields = '__all__'

class TopScorerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopScorer
        fields = '__all__'

class PlayerSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source='team.name', read_only=True)
    
    class Meta:
        model = Player
        fields = ['id', 'name', 'position', 'nationality', 'team', 'team_name', 
                 'shirt_number', 'age', 'market_value']

# Nested serializers for detailed views
class TeamDetailSerializer(serializers.ModelSerializer):
    home_matches = MatchSerializer(many=True, read_only=True)
    away_matches = MatchSerializer(many=True, read_only=True)
    
    class Meta:
        model = Team
        fields = '__all__'

class MatchDetailSerializer(serializers.ModelSerializer):
    home_team = TeamSerializer(read_only=True)
    away_team = TeamSerializer(read_only=True)
    competition = CompetitionSerializer(read_only=True)
    prediction = MatchPredictionSerializer(source='matchprediction', read_only=True)
    betting_odds = BettingOddsSerializer(many=True, read_only=True)
    formations = TeamFormationSerializer(many=True, read_only=True)
    
    class Meta:
        model = Match
        fields = '__all__'

class PlayerStatsDetailSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True)
    match = MatchSerializer(read_only=True)
    
    class Meta:
        model = PlayerStats
        fields = '__all__'
