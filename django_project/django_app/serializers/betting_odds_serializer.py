from rest_framework import serializers
from ..models import BettingOdds

class BettingOddsSerializer(serializers.ModelSerializer):
    match_details = serializers.CharField(source='match.__str__', read_only=True)
    home_team = serializers.CharField(source='match.home_team.name', read_only=True)
    away_team = serializers.CharField(source='match.away_team.name', read_only=True)
    competition = serializers.CharField(source='match.competition.name', read_only=True)

    class Meta:
        model = BettingOdds
        fields = [
            'id', 'match', 'match_details', 'home_team', 'away_team', 'competition',
            'home_win_odds', 'draw_odds', 'away_win_odds', 'last_updated'
        ]
