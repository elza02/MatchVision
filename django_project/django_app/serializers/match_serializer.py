from rest_framework import serializers
from ..models import Match

class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = '__all__'

class MatchDetailSerializer(serializers.ModelSerializer):
    home_team_name = serializers.CharField(source='home_team.name', read_only=True)
    away_team_name = serializers.CharField(source='away_team.name', read_only=True)
    competition_name = serializers.CharField(source='competition.name', read_only=True)

    class Meta:
        model = Match
        fields = '__all__'
