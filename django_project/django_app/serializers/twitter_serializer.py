from rest_framework import serializers
from ..models import TwitterFeed

class TwitterFeedSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source='related_team.name', read_only=True)
    competition_name = serializers.CharField(source='related_competition.name', read_only=True)

    class Meta:
        model = TwitterFeed
        fields = [
            'tweet_id',
            'content',
            'author',
            'author_username',
            'author_profile_image',
            'created_at',
            'likes_count',
            'retweets_count',
            'media_urls',
            'category',
            'team_name',
            'competition_name'
        ]
