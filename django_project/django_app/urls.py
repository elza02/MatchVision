from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TeamViewSet, CompetitionViewSet, MatchViewSet,
    PlayerStatsViewSet, MatchPredictionViewSet, PlayerViewSet,
    TeamFormationViewSet, BettingOddsViewSet, TopScorerViewSet,
    dashboard_stats, dashboard_upcoming_matches, dashboard_top_scorers,
    # TwitterFeedViewSet,
    AnalyticsViewSet
)

# Create a router and register our viewsets with it.
router = DefaultRouter()

# Register core viewsets
router.register(r'teams', TeamViewSet)
router.register(r'competitions', CompetitionViewSet)
router.register(r'matches', MatchViewSet)
router.register(r'players', PlayerViewSet)
router.register(r'player-stats', PlayerStatsViewSet)
router.register(r'match-predictions', MatchPredictionViewSet)
router.register(r'team-formations', TeamFormationViewSet)
router.register(r'betting-odds', BettingOddsViewSet)
router.register(r'top-scorers', TopScorerViewSet)

# Register Twitter viewset separately
# router.register(r'twitter', TwitterFeedViewSet, basename='twitter')

# Analytics URLs
router.register(r'analytics', AnalyticsViewSet, basename='analytics')

# Register the analytics URLs with custom actions
analytics_urls = [
    path('analytics/competition/<int:competition_id>/', 
         AnalyticsViewSet.as_view({'get': 'get_competition_analytics'}), 
         name='competition-analytics'),
    path('analytics/team/<int:team_id>/', 
         AnalyticsViewSet.as_view({'get': 'get_team_analytics'}), 
         name='team-analytics'),
    path('analytics/player/<int:player_id>/', 
         AnalyticsViewSet.as_view({'get': 'get_player_analytics'}), 
         name='player-analytics'),
]

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
    *analytics_urls,
    # Dashboard specific endpoints
    path('dashboard/stats/', dashboard_stats, name='dashboard-stats'),
    path('dashboard/upcoming-matches/', dashboard_upcoming_matches, name='dashboard-upcoming-matches'),
    path('dashboard/top-scorers/', dashboard_top_scorers, name='dashboard-top-scorers'),
]
