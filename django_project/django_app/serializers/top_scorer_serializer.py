from rest_framework import serializers
from ..models import TopScorer

class TopScorerSerializer(serializers.ModelSerializer):
    competition_name = serializers.CharField(source='competition.name', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)

    class Meta:
        model = TopScorer
        fields = [
            'id', 'player_name', 'team', 'team_name', 'competition',
            'competition_name', 'goals', 'assists', 'matches_played',
            'minutes_played', 'season'
        ]
