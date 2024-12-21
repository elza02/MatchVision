from rest_framework import serializers
from .models import Team, Competition, Match, TopScorer, Standing, Coach, Player, Area

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'
        
class CompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = '__all__'

class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = '__all__'
        

class TopScorerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopScorer
        fields = '__all__'
        

class StandingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Standing
        fields = '__all__'
        

class CoachSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coach
        fields = '__all__'
        

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = '__all__'
        

class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = '__all__'
        
