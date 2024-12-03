from rest_framework import serializers
from ..models import PlayerStats

class PlayerStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerStats
        fields = '__all__'

class PlayerStatsDetailSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source='team.name', read_only=True)

    class Meta:
        model = PlayerStats
        fields = '__all__'
