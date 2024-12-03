from rest_framework import serializers
from ..models import MatchPrediction

class MatchPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchPrediction
        fields = '__all__'
