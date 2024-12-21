from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TeamViewSet, CompetitionViewSet, MatchViewSet

# Initialize the router
router = DefaultRouter()

# Register the viewsets
router.register(r'teams', TeamViewSet, basename='team')
router.register(r'competitions', CompetitionViewSet, basename='competition')
router.register(r'matches', MatchViewSet, basename='match')

# Define the URL patterns
urlpatterns = [
    path('', include(router.urls)),  # Include the automatically generated URLs
]
