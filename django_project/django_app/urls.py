from django.urls import path
from .views import (
    DashboardStatsView,
    DashboardMatchesView,
    DashboardScorersView,
    MatchListView,
    MatchDetailView,
    TeamListView,
    TeamDetailView,
    PlayerListView,
    PlayerDetailView,
    CompetitionListView,
    CompetitionDetailView,
    MatchPredictionsView,
    CompetitionAnalyticsView,
    TeamAnalyticsView,
    PlayerAnalyticsView,
    MatchAnalyticsView,
    TeamComparisonView
)

urlpatterns = [
    # Dashboard endpoints
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('dashboard/upcoming-matches/', DashboardMatchesView.as_view(), name='dashboard-matches'),
    path('dashboard/top-scorers/', DashboardScorersView.as_view(), name='dashboard-scorers'),

    # Matches
    path('matches/', MatchListView.as_view(), name='match-list'),
    path('matches/<int:pk>/', MatchDetailView.as_view(), name='match-detail'),

    # Teams
    path('teams/', TeamListView.as_view(), name='team-list'),
    path('teams/<int:pk>/', TeamDetailView.as_view(), name='team-detail'),

    # Players
    path('players/', PlayerListView.as_view(), name='player-list'),
    path('players/<int:pk>/', PlayerDetailView.as_view(), name='player-detail'),

    # Competitions
    path('competitions/', CompetitionListView.as_view(), name='competition-list'),
    path('competitions/<int:pk>/', CompetitionDetailView.as_view(), name='competition-detail'),

    # Predictions
    path('match-predictions/', MatchPredictionsView.as_view(), name='match-predictions'),

    # Analytics
    path('analytics/competition/<int:competition_id>/', CompetitionAnalyticsView.as_view(), name='competition-analytics'),
    path('analytics/team/<int:team_id>/', TeamAnalyticsView.as_view(), name='team-analytics'),
    path('analytics/player/<int:player_id>/', PlayerAnalyticsView.as_view(), name='player-analytics'),
    path('analytics/match/<int:match_id>/', MatchAnalyticsView.as_view(), name='match-analytics'),
    path('analytics/team-comparison/<int:team1_id>/<int:team2_id>/', TeamComparisonView.as_view(), name='team-comparison'),
]
