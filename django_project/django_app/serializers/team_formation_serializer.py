from rest_framework import serializers
from ..models import TeamFormation

class TeamFormationSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source='team.name', read_only=True)
    competition_name = serializers.CharField(source='competition.name', read_only=True)

    class Meta:
        model = TeamFormation
        fields = ['id', 'team', 'team_name', 'competition', 'competition_name', 'formation', 'match_date']
