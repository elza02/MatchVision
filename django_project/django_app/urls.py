from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('dashboard/stats/', views.DashboardStatsView.as_view(), name='dashboard-stats'),
    path('dashboard/upcoming-matches/', views.DashboardMatchesView.as_view(), name='dashboard-matches'),
    path('dashboard/top-scorers/', views.DashboardScorersView.as_view(), name='dashboard-scorers'),
    
    # Teams
    path('teams/', views.TeamListView.as_view(), name='team-list'),
    path('teams/<int:pk>/', views.TeamDetailView.as_view(), name='team-detail'),
    
    # Players
    path('players/', views.PlayerListView.as_view(), name='player-list'),
    path('players/<int:pk>/', views.PlayerDetailView.as_view(), name='player-detail'),
    
    # Matches
    path('matches/', views.MatchListView.as_view(), name='match-list'),
    path('matches/<int:pk>/', views.MatchDetailView.as_view(), name='match-detail'),
    
    # Competitions
    path('competitions/', views.CompetitionListView.as_view(), name='competition-list'),
    path('competitions/<int:pk>/', views.CompetitionDetailView.as_view(), name='competition-detail'),

    # Analytics endpoints
    path('analytics/overview/', views.AnalyticsOverviewView.as_view(), name='analytics-overview'),
    path('analytics/team/<int:team_id>/', views.TeamAnalyticsView.as_view(), name='team-analytics'),
]
