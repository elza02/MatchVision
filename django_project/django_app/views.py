from django.db.models import Q, F, Count, Avg, Sum, Case, When, FloatField
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from django_filters.rest_framework import DjangoFilterBackend

from .models import Team, Competition, Match, Player, TopScorer, Standing, Coach, Area
from .serializers import (TeamSerializer, CompetitionSerializer, MatchSerializer, 
                        TopScorerSerializer)

import logging
logger = logging.getLogger(__name__)

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'venue']
    
    @action(detail=True)
    def statistics(self, request, pk=None):
        try:
            team = self.get_object()
            
            # Get matches
            home_matches = Match.objects.filter(home_team=team)
            away_matches = Match.objects.filter(away_team=team)
            
            # Calculate home performance
            home_stats = home_matches.aggregate(
                matches_played=Count('id'),
                goals_scored=Coalesce(Sum('home_team_score'), 0),
                goals_conceded=Coalesce(Sum('away_team_score'), 0),
                wins=Count('id', filter=Q(home_team_score__gt=F('away_team_score'))),
                draws=Count('id', filter=Q(home_team_score=F('away_team_score'))),
                losses=Count('id', filter=Q(home_team_score__lt=F('away_team_score')))
            )
            
            # Calculate away performance
            away_stats = away_matches.aggregate(
                matches_played=Count('id'),
                goals_scored=Coalesce(Sum('away_team_score'), 0),
                goals_conceded=Coalesce(Sum('home_team_score'), 0),
                wins=Count('id', filter=Q(away_team_score__gt=F('home_team_score'))),
                draws=Count('id', filter=Q(away_team_score=F('home_team_score'))),
                losses=Count('id', filter=Q(away_team_score__lt=F('home_team_score')))
            )
            
            # Get top scorers from TopScorer model
            top_scorers = TopScorer.objects.filter(team=team)\
                .select_related('player')\
                .order_by('-goals', '-assists')[:5]
            
            # Get current standings
            current_standing = Standing.objects.filter(team=team)\
                .select_related('competition')\
                .order_by('-season')\
                .first()
            
            # Get coach information
            coach_info = None
            if team.coach:
                coach_info = {
                    'name': team.coach.name,
                    'nationality': team.coach.nationality,
                    'contract_start': team.coach.contract_start_date,
                    'contract_end': team.coach.contract_end_date
                }
            
            stats = {
                'team_info': {
                    'name': team.name,
                    'founded': team.founded,
                    'venue': team.venue,
                    'colors': team.club_colors,
                    'coach': coach_info
                },
                'overall': {
                    'matches_played': home_stats['matches_played'] + away_stats['matches_played'],
                    'wins': home_stats['wins'] + away_stats['wins'],
                    'draws': home_stats['draws'] + away_stats['draws'],
                    'losses': home_stats['losses'] + away_stats['losses'],
                    'goals_scored': home_stats['goals_scored'] + away_stats['goals_scored'],
                    'goals_conceded': home_stats['goals_conceded'] + away_stats['goals_conceded'],
                    'goal_difference': (home_stats['goals_scored'] + away_stats['goals_scored']) - 
                                     (home_stats['goals_conceded'] + away_stats['goals_conceded']),
                    'points': (home_stats['wins'] + away_stats['wins']) * 3 + 
                             (home_stats['draws'] + away_stats['draws'])
                },
                'home_performance': home_stats,
                'away_performance': away_stats,
                'top_scorers': [{
                    'player_name': scorer.player.name,
                    'goals': scorer.goals,
                    'assists': scorer.assists,
                    'penalties': scorer.penalties,
                    'matches_played': scorer.played_matches
                } for scorer in top_scorers],
                'current_standing': {
                    'position': current_standing.position if current_standing else None,
                    'points': current_standing.points if current_standing else None,
                    'competition': current_standing.competition.name if current_standing else None,
                    'form': current_standing.form if current_standing else None
                } if current_standing else None
            }
            
            return Response(stats)
            
        except Exception as e:
            logger.error(f"Error in team statistics: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CompetitionViewSet(viewsets.ModelViewSet):
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name']
    
    @action(detail=True)
    def standings(self, request, pk=None):
        try:
            competition = self.get_object()
            season = request.query_params.get('season', None)
            
            standings = Standing.objects.filter(
                competition=competition,
                season=season if season else competition.area.name
            ).select_related('team').order_by('position')
            
            standings_data = [{
                'position': standing.position,
                'team': {
                    'name': standing.team.name,
                    'crest': standing.team.crest
                },
                'played': standing.played_games,
                'won': standing.won,
                'drawn': standing.draw,
                'lost': standing.lost,
                'goals_for': standing.goals_for,
                'goals_against': standing.goals_against,
                'goal_difference': standing.goal_difference,
                'points': standing.points,
                'form': list(standing.form) if standing.form else []
            } for standing in standings]
            
            return Response(standings_data)
            
        except Exception as e:
            logger.error(f"Error in competition standings: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True)
    def top_scorers(self, request, pk=None):
        try:
            competition = self.get_object()
            season = request.query_params.get('season', None)
            
            scorers = TopScorer.objects.filter(
                competition=competition,
                season=season if season else competition.area.name
            ).select_related('player', 'team').order_by('-goals', '-assists')[:10]
            
            scorers_data = [{
                'player': {
                    'name': scorer.player.name,
                    'nationality': scorer.player.nationality,
                    'position': scorer.player.position
                },
                'team': {
                    'name': scorer.team.name,
                    'crest': scorer.team.crest
                },
                'stats': {
                    'matches_played': scorer.played_matches,
                    'goals': scorer.goals,
                    'assists': scorer.assists,
                    'penalties': scorer.penalties
                }
            } for scorer in scorers]
            
            return Response(scorers_data)
            
        except Exception as e:
            logger.error(f"Error in competition top scorers: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class MatchViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.select_related('home_team', 'away_team', 'competition').all()
    serializer_class = MatchSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['competition', 'status', 'season']
    search_fields = ['home_team__name', 'away_team__name']
    pagination_class = PageNumberPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        competition_id = self.request.query_params.get('competition', None)
        
        if competition_id:
            queryset = queryset.filter(competition_id=competition_id)
        
        return queryset.order_by('-match_date')
    
    @action(detail=True)
    def match_analysis(self, request, pk=None):
        try:
            match = self.get_object()
            
            # Get head to head history
            h2h_matches = Match.objects.filter(
                Q(home_team=match.home_team, away_team=match.away_team) |
                Q(home_team=match.away_team, away_team=match.home_team)
            ).order_by('-match_date')[:5]
            
            # Get team standings
            home_standing = Standing.objects.filter(
                team=match.home_team,
                competition=match.competition,
                season=match.season
            ).first()
            
            away_standing = Standing.objects.filter(
                team=match.away_team,
                competition=match.competition,
                season=match.season
            ).first()
            
            analysis = {
                'match_details': {
                    'date': match.match_date,
                    'competition': match.competition.name,
                    'status': match.status,
                    'stage': match.stage,
                    'score': {
                        'home': match.home_team_score,
                        'away': match.away_team_score
                    }
                },
                'home_team': {
                    'name': match.home_team.name,
                    'standing': {
                        'position': home_standing.position if home_standing else None,
                        'points': home_standing.points if home_standing else None,
                        'form': list(home_standing.form) if home_standing and home_standing.form else []
                    } if home_standing else None
                },
                'away_team': {
                    'name': match.away_team.name,
                    'standing': {
                        'position': away_standing.position if away_standing else None,
                        'points': away_standing.points if away_standing else None,
                        'form': list(away_standing.form) if away_standing and away_standing.form else []
                    } if away_standing else None
                },
                'head_to_head': [{
                    'date': h2h.match_date,
                    'home_team': h2h.home_team.name,
                    'away_team': h2h.away_team.name,
                    'score': {
                        'home': h2h.home_team_score,
                        'away': h2h.away_team_score
                    }
                } for h2h in h2h_matches]
            }
            
            return Response(analysis)
            
        except Exception as e:
            logger.error(f"Error in match analysis: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )