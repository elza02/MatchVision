from rest_framework import serializers
from .models import (
    Team, Competition, Match, PlayerStats, Player, 
    MatchPrediction, TeamFormation, BettingOdds, TopScorer
)

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'

class CompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = '__all__'


class MatchSerializer(serializers.ModelSerializer):
    home_team = TeamSerializer(read_only=True)
    away_team = TeamSerializer(read_only=True)
    
    # Optional: Keep the name fields if you want them separately
    home_team_name = serializers.CharField(source='home_team.name', read_only=True)
    away_team_name = serializers.CharField(source='away_team.name', read_only=True)
    
    # Write-only fields for creating/updating matches
    home_team_id = serializers.PrimaryKeyRelatedField(
        queryset=Team.objects.all(), 
        source='home_team', 
        write_only=True
    )
    away_team_id = serializers.PrimaryKeyRelatedField(
        queryset=Team.objects.all(), 
        source='away_team', 
        write_only=True
    )
    competition_id = serializers.PrimaryKeyRelatedField(
        queryset=Competition.objects.all(), 
        source='competition', 
        write_only=True
    )

    class Meta:
        model = Match
        fields = '__all__'  # This will now include all match fields AND full team details
        depth = 1  # Optional: can help with nested serialization

    def to_representation(self, instance):
        print("\n--- Match Serialization Debug ---")
        print(f"Match ID: {instance.id}")
        print(f"Home Team: {instance.home_team}")
        print(f"Away Team: {instance.away_team}")
        
        representation = super().to_representation(instance)
        print("\nFull Representation:")
        print(representation)
        return representation



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
