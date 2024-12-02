from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TeamViewSet, CompetitionViewSet, MatchViewSet,
    PlayerStatsViewSet, MatchPredictionViewSet, PlayerViewSet,
    TeamFormationViewSet, BettingOddsViewSet, TopScorerViewSet,
    dashboard_stats, dashboard_upcoming_matches, dashboard_top_scorers
)

router = DefaultRouter()
router.register(r'teams', TeamViewSet)
router.register(r'competitions', CompetitionViewSet)
router.register(r'matches', MatchViewSet)
router.register(r'players', PlayerViewSet)
router.register(r'player-stats', PlayerStatsViewSet)
router.register(r'match-predictions', MatchPredictionViewSet)
router.register(r'team-formations', TeamFormationViewSet)
router.register(r'betting-odds', BettingOddsViewSet)
router.register(r'top-scorers', TopScorerViewSet)

urlpatterns = [
    path('', include(router.urls)),  # Remove 'api/' prefix since it's already in project urls.py
    # Dashboard specific endpoints
    path('dashboard/stats/', dashboard_stats, name='dashboard-stats'),
    path('dashboard/upcoming-matches/', dashboard_upcoming_matches, name='dashboard-upcoming-matches'),
    path('dashboard/top-scorers/', dashboard_top_scorers, name='dashboard-top-scorers'),
]
