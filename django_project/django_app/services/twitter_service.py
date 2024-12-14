# import tweepy
# import json
# from datetime import datetime
# from django.conf import settings
# from ..models import TwitterFeed, Team, Competition
# import logging

# logger = logging.getLogger(__name__)

# class TwitterService:
#     def __init__(self):
#         self.api = tweepy.Client(
#             bearer_token=settings.TWITTER_BEARER_TOKEN,
#             consumer_key=settings.TWITTER_API_KEY,
#             consumer_secret=settings.TWITTER_API_SECRET,
#             access_token=settings.TWITTER_ACCESS_TOKEN,
#             access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET
#         )
#         self.auth = tweepy.OAuth1UserHandler(
#             settings.TWITTER_API_KEY,
#             settings.TWITTER_API_SECRET,
#             settings.TWITTER_ACCESS_TOKEN,
#             settings.TWITTER_ACCESS_TOKEN_SECRET
#         )
#         self.api_v1 = tweepy.API(self.auth)

#     def _categorize_tweet(self, tweet_text):
#         text_lower = tweet_text.lower()
#         if any(word in text_lower for word in ['transfer', 'sign', 'deal', 'contract']):
#             return 'TRANSFER'
#         elif any(word in text_lower for word in ['goal', 'score', 'match', 'game', 'vs', 'final']):
#             return 'MATCH'
#         elif any(word in text_lower for word in ['highlight', 'watch', 'video', 'clip']):
#             return 'HIGHLIGHT'
#         elif any(word in text_lower for word in ['news', 'update', 'report', 'official']):
#             return 'NEWS'
#         return 'OTHER'

#     def _find_related_entities(self, tweet_text):
#         related_team = None
#         related_competition = None

#         # Try to find related team
#         teams = Team.objects.all()
#         for team in teams:
#             if team.name.lower() in tweet_text.lower():
#                 related_team = team
#                 break

#         # Try to find related competition
#         competitions = Competition.objects.all()
#         for competition in competitions:
#             if competition.name.lower() in tweet_text.lower():
#                 related_competition = competition
#                 break

#         return related_team, related_competition

#     def fetch_and_store_tweets(self, query, max_results=10):
#         try:
#             tweets = self.api.search_recent_tweets(
#                 query=query,
#                 max_results=max_results,
#                 tweet_fields=['created_at', 'public_metrics', 'author_id'],
#                 expansions=['author_id', 'attachments.media_keys'],
#                 media_fields=['url', 'preview_image_url']
#             )

#             if not tweets.data:
#                 return []

#             stored_tweets = []
#             for tweet in tweets.data:
#                 # Get author info
#                 author = next((user for user in tweets.includes['users'] if user.id == tweet.author_id), None)
                
#                 # Get media URLs
#                 media_urls = []
#                 if hasattr(tweet, 'attachments') and 'media_keys' in tweet.attachments:
#                     media_keys = tweet.attachments['media_keys']
#                     for media in tweets.includes.get('media', []):
#                         if media.media_key in media_keys:
#                             media_urls.append(media.url or media.preview_image_url)

#                 # Find related entities
#                 related_team, related_competition = self._find_related_entities(tweet.text)

#                 # Create or update tweet
#                 tweet_obj, created = TwitterFeed.objects.update_or_create(
#                     tweet_id=tweet.id,
#                     defaults={
#                         'content': tweet.text,
#                         'author': author.name if author else '',
#                         'author_username': author.username if author else '',
#                         'author_profile_image': author.profile_image_url if author else None,
#                         'created_at': tweet.created_at,
#                         'likes_count': tweet.public_metrics['like_count'],
#                         'retweets_count': tweet.public_metrics['retweet_count'],
#                         'media_urls': media_urls,
#                         'category': self._categorize_tweet(tweet.text),
#                         'related_team': related_team,
#                         'related_competition': related_competition
#                     }
#                 )
#                 stored_tweets.append(tweet_obj)

#             return stored_tweets

#         except Exception as e:
#             logger.error(f"Error fetching tweets: {str(e)}")
#             return []

#     def get_trending_tweets(self, category=None, team=None, competition=None):
#         queryset = TwitterFeed.objects.all()

#         if category:
#             queryset = queryset.filter(category=category)
#         if team:
#             queryset = queryset.filter(related_team=team)
#         if competition:
#             queryset = queryset.filter(related_competition=competition)

#         return queryset.order_by('-created_at', '-likes_count')[:20]
