from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Avg, Sum, F, Q, FloatField, Case, When, Value
from django.db.models.functions import Cast, Coalesce
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from .models import (
    Team, Competition, Match, PlayerStats, Player,
    MatchPrediction, TeamFormation, BettingOdds, TopScorer
)
from .serializers import (
    TeamSerializer, CompetitionSerializer, MatchSerializer,
    PlayerStatsSerializer, MatchPredictionSerializer,
    TeamFormationSerializer, BettingOddsSerializer, TopScorerSerializer,
    TeamDetailSerializer, MatchDetailSerializer, PlayerStatsDetailSerializer,
    PlayerSerializer
)
from rest_framework.pagination import PageNumberPagination
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
            if not team:
                return Response(
                    {"error": "Team not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            home_matches = Match.objects.filter(home_team=team)
            away_matches = Match.objects.filter(away_team=team)
            
            # Calculate home performance
            home_stats = home_matches.aggregate(
                matches_played=Count('id'),
                goals_scored=Sum('home_team_score'),
                goals_conceded=Sum('away_team_score'),
                wins=Count('id', filter=Q(home_team_score__gt=F('away_team_score'))),
                draws=Count('id', filter=Q(home_team_score=F('away_team_score'))),
                losses=Count('id', filter=Q(home_team_score__lt=F('away_team_score')))
            )
            
            # Calculate away performance
            away_stats = away_matches.aggregate(
                matches_played=Count('id'),
                goals_scored=Sum('away_team_score'),
                goals_conceded=Sum('home_team_score'),
                wins=Count('id', filter=Q(away_team_score__gt=F('home_team_score'))),
                draws=Count('id', filter=Q(away_team_score=F('home_team_score'))),
                losses=Count('id', filter=Q(away_team_score__lt=F('home_team_score')))
            )
            
            # Get top scorers
            top_scorers = PlayerStats.objects.filter(team=team)\
                .values('name')\
                .annotate(
                    total_goals=Sum('goals'),
                    total_assists=Sum('assists'),
                    matches_played=Count('match'),
                    avg_minutes=Avg('minutes_played')
                ).order_by('-total_goals')[:5]
            
            # Get team formation analysis
            formations = TeamFormation.objects.filter(team=team)\
                .values('formation')\
                .annotate(count=Count('id'))\
                .order_by('-count')
            
            # Calculate market value statistics
            value_stats = Player.objects.filter(team=team).aggregate(
                total_value=Sum('market_value'),
                avg_value=Avg('market_value'),
                squad_size=Count('id')
            )
            
            stats = {
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
                'home': home_stats,
                'away': away_stats,
                'top_scorers': list(top_scorers),
                'formations': list(formations),
                'squad': {
                    'size': value_stats['squad_size'],
                    'total_market_value': value_stats['total_value'],
                    'average_player_value': value_stats['avg_value'],
                    'positions': Player.objects.filter(team=team)
                        .values('position')
                        .annotate(count=Count('id'))
                }
            }
            return Response(stats)
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CompetitionViewSet(viewsets.ModelViewSet):
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'country']
    
    @action(detail=True)
    def standings(self, request, pk=None):
        try:
            competition = self.get_object()
            if not competition:
                return Response(
                    {"error": "Competition not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            matches = Match.objects.filter(competition=competition)
            
            # If no matches found, return empty standings
            if not matches.exists():
                return Response([])
            
            teams = Team.objects.filter(
                Q(home_matches__competition=competition) |
                Q(away_matches__competition=competition)
            ).distinct()
            
            # If no teams found, return empty standings
            if not teams.exists():
                return Response([])
            
            standings = []
            for team in teams:
                try:
                    home_matches = matches.filter(home_team=team)
                    away_matches = matches.filter(away_team=team)
                    
                    home_stats = home_matches.aggregate(
                        played=Count('id'),
                        wins=Count('id', filter=Q(home_team_score__gt=F('away_team_score'))),
                        draws=Count('id', filter=Q(home_team_score=F('away_team_score'))),
                        losses=Count('id', filter=Q(home_team_score__lt=F('away_team_score'))),
                        goals_for=Coalesce(Sum(Coalesce('home_team_score', 0)), 0),
                        goals_against=Coalesce(Sum(Coalesce('away_team_score', 0)), 0)
                    )
                    
                    away_stats = away_matches.aggregate(
                        played=Count('id'),
                        wins=Count('id', filter=Q(away_team_score__gt=F('home_team_score'))),
                        draws=Count('id', filter=Q(away_team_score=F('home_team_score'))),
                        losses=Count('id', filter=Q(away_team_score__lt=F('home_team_score'))),
                        goals_for=Coalesce(Sum(Coalesce('away_team_score', 0)), 0),
                        goals_against=Coalesce(Sum(Coalesce('home_team_score', 0)), 0)
                    )
                    
                    stats = {
                        'team': TeamSerializer(team).data,
                        'matches_played': home_stats['played'] + away_stats['played'],
                        'wins': home_stats['wins'] + away_stats['wins'],
                        'draws': home_stats['draws'] + away_stats['draws'],
                        'losses': home_stats['losses'] + away_stats['losses'],
                        'goals_for': home_stats['goals_for'] + away_stats['goals_for'],
                        'goals_against': home_stats['goals_against'] + away_stats['goals_against'],
                        'goal_difference': (home_stats['goals_for'] + away_stats['goals_for']) -
                                         (home_stats['goals_against'] + away_stats['goals_against']),
                        'points': (home_stats['wins'] + away_stats['wins']) * 3 +
                                 (home_stats['draws'] + away_stats['draws']),
                        'form': []  # Initialize empty form
                    }
                    
                    # Get team form only if there are recent matches
                    recent_matches = matches.filter(
                        Q(home_team=team) | Q(away_team=team),
                        status='FINISHED'  # Only consider finished matches for form
                    ).order_by('-match_date')[:5]
                    
                    if recent_matches.exists():
                        stats['form'] = self._get_team_form(team, recent_matches)
                    
                    standings.append(stats)
                except Exception as team_error:
                    print(f"Error processing team {team.name}: {str(team_error)}")
                    continue  # Skip this team if there's an error
            
            if not standings:
                return Response([])
            
            # Sort standings by points, goal difference, and goals scored
            sorted_standings = sorted(
                standings,
                key=lambda x: (x['points'], x['goal_difference'], x['goals_for']),
                reverse=True
            )
            
            return Response(sorted_standings)
            
        except Exception as e:
            print(f"Error in standings view: {str(e)}")
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_team_form(self, team, recent_matches):
        form = []
        for match in recent_matches:
            if match.home_team == team:
                if match.home_team_score > match.away_team_score:
                    form.append('W')
                elif match.home_team_score < match.away_team_score:
                    form.append('L')
                else:
                    form.append('D')
            else:
                if match.away_team_score > match.home_team_score:
                    form.append('W')
                elif match.away_team_score < match.home_team_score:
                    form.append('L')
                else:
                    form.append('D')
        return form

    @action(detail=True)
    def statistics(self, request, pk=None):
        try:
            competition = self.get_object()
            if not competition:
                return Response(
                    {"error": "Competition not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            matches = Match.objects.filter(competition=competition)
            
            # Calculate basic statistics
            match_stats = matches.aggregate(
                total_matches=Count('id'),
                matches_played=Count('id', filter=Q(status='FINISHED')),
                goals_scored=Coalesce(Sum('home_team_score'), 0) + Coalesce(Sum('away_team_score'), 0),
            )
            
            # Calculate average goals per match
            if match_stats['matches_played'] > 0:
                match_stats['avg_goals_per_match'] = round(
                    float(match_stats['goals_scored']) / float(match_stats['matches_played']), 2
                )
            else:
                match_stats['avg_goals_per_match'] = 0
                
            # Get top scorers
            top_scorers = PlayerStats.objects.filter(match__competition=competition)\
                .values('name')\
                .annotate(
                    goals=Sum('goals'),
                    matches=Count('match', distinct=True)
                ).order_by('-goals')[:5]
            
            # Get team statistics
            team_stats = {
                'most_goals': [],
                'best_defense': []
            }
            
            # Calculate team goals
            team_goals = []
            teams = Team.objects.filter(
                Q(home_matches__competition=competition) | 
                Q(away_matches__competition=competition)
            ).distinct()
            
            for team in teams:
                home_goals = matches.filter(home_team=team).aggregate(
                    goals=Coalesce(Sum('home_team_score'), 0)
                )['goals']
                away_goals = matches.filter(away_team=team).aggregate(
                    goals=Coalesce(Sum('away_team_score'), 0)
                )['goals']
                
                home_conceded = matches.filter(home_team=team).aggregate(
                    goals=Coalesce(Sum('away_team_score'), 0)
                )['goals']
                away_conceded = matches.filter(away_team=team).aggregate(
                    goals=Coalesce(Sum('home_team_score'), 0)
                )['goals']
                
                team_goals.append({
                    'team': TeamSerializer(team).data,
                    'total_goals': home_goals + away_goals,
                    'goals_conceded': home_conceded + away_conceded
                })
            
            # Sort teams by goals scored and conceded
            team_goals.sort(key=lambda x: x['total_goals'], reverse=True)
            team_stats['most_goals'] = team_goals[:5]
            
            team_goals.sort(key=lambda x: x['goals_conceded'])
            team_stats['best_defense'] = team_goals[:5]
            
            stats = {
                **match_stats,
                'top_scorers': list(top_scorers),
                'team_stats': team_stats
            }
            
            return Response(stats)
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class MatchViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.select_related('home_team', 'away_team', 'competition').all()
    serializer_class = MatchSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['competition', 'home_team', 'away_team', 'status', 'season']
    search_fields = ['home_team__name', 'away_team__name']
    pagination_class = PageNumberPagination

    def get_queryset(self):
        try:
            queryset = super().get_queryset()
            competition_id = self.request.query_params.get('competition', None)
            page_size = self.request.query_params.get('page_size', 12)
            
            # Validate page_size
            try:
                page_size = int(page_size)
                if page_size < 1:
                    page_size = 12
            except (TypeError, ValueError):
                page_size = 12
            
            # Set pagination page size dynamically
            self.pagination_class.page_size = page_size
            
            if competition_id:
                queryset = queryset.filter(competition_id=competition_id)
            
            # Optimize query with select_related and only needed fields
            queryset = queryset.select_related(
                'home_team',
                'away_team',
                'competition'
            ).only(
                'id',
                'match_date',
                'status',
                'home_team_score',
                'away_team_score',
                'home_team__name',
                'away_team__name',
                'competition__name'
            ).order_by('-match_date')
            
            return queryset
            
        except Exception as e:
            logger.error(f"Error in MatchViewSet.get_queryset: {str(e)}")
            return Match.objects.none()
    
    def perform_create(self, serializer):
        try:
            with transaction.atomic():
                # Validate match date
                match_date = serializer.validated_data.get('match_date')
                if match_date and match_date < timezone.now():
                    raise ValidationError("Match date cannot be in the past")
                
                # Validate scores
                home_score = serializer.validated_data.get('home_team_score')
                away_score = serializer.validated_data.get('away_team_score')
                if home_score is not None and home_score < 0:
                    raise ValidationError("Home team score cannot be negative")
                if away_score is not None and away_score < 0:
                    raise ValidationError("Away team score cannot be negative")
                
                serializer.save()
        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": "An error occurred while creating the match"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MatchDetailSerializer
        return MatchSerializer

    @action(detail=True)
    def match_analysis(self, request, pk=None):
        try:
            match = self.get_object()
            if not match:
                return Response(
                    {"error": "Match not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get head to head history
            h2h = self._get_head_to_head(match.home_team, match.away_team)
            
            # Get team stats
            home_team_stats = self._get_team_stats(match.home_team)
            away_team_stats = self._get_team_stats(match.away_team)
            
            # Get player stats for this match
            player_stats = PlayerStats.objects.filter(match=match)\
                .select_related('team')\
                .order_by('-goals', '-assists')
            
            # Get match prediction if available
            try:
                prediction = MatchPrediction.objects.get(match=match)
                prediction_data = MatchPredictionSerializer(prediction).data
            except MatchPrediction.DoesNotExist:
                prediction_data = None
            
            # Get team formations if available
            formations = TeamFormation.objects.filter(match=match)\
                .select_related('team')
            
            analysis = {
                'match_details': MatchSerializer(match).data,
                'head_to_head': h2h,
                'home_team_stats': home_team_stats,
                'away_team_stats': away_team_stats,
                'player_stats': PlayerStatsSerializer(player_stats, many=True).data,
                'prediction': prediction_data,
                'formations': TeamFormationSerializer(formations, many=True).data,
            }
            
            return Response(analysis)
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _get_head_to_head(self, home_team, away_team):
        h2h_matches = Match.objects.filter(
            Q(home_team=home_team, away_team=away_team) |
            Q(home_team=away_team, away_team=home_team)
        ).order_by('-match_date')[:5]
        
        return MatchSerializer(h2h_matches, many=True).data

    def _get_team_stats(self, team):
        recent_matches = Match.objects.filter(
            Q(home_team=team) | Q(away_team=team)
        ).order_by('-match_date')[:5]
        
        stats = {
            'recent_form': [],
            'goals_scored': 0,
            'goals_conceded': 0,
            'clean_sheets': 0
        }
        
        for match in recent_matches:
            if match.status == 'FINISHED':
                if match.home_team == team:
                    goals_for = match.home_team_score
                    goals_against = match.away_team_score
                else:
                    goals_for = match.away_team_score
                    goals_against = match.home_team_score
                
                stats['goals_scored'] += goals_for
                stats['goals_conceded'] += goals_against
                
                if goals_against == 0:
                    stats['clean_sheets'] += 1
                
                if goals_for > goals_against:
                    stats['recent_form'].append('W')
                elif goals_for < goals_against:
                    stats['recent_form'].append('L')
                else:
                    stats['recent_form'].append('D')
        
        return stats

    @action(detail=True)
    def statistics(self, request, pk=None):
        try:
            match = self.get_object()
            if not match:
                return Response(
                    {"error": "Match not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            stats = {
                'match_info': {
                    'competition': match.competition.name,
                    'date': match.match_date,
                    'status': match.status,
                    'venue': match.home_team.venue,
                },
                'scores': {
                    'home_team': {
                        'name': match.home_team.name,
                        'score': match.home_team_score or 0
                    },
                    'away_team': {
                        'name': match.away_team.name,
                        'score': match.away_team_score or 0
                    }
                }
            }

            # Get player statistics
            player_stats = PlayerStats.objects.filter(match=match)
            stats['player_stats'] = PlayerStatsSerializer(player_stats, many=True).data

            return Response(stats)
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PlayerStatsViewSet(viewsets.ModelViewSet):
    queryset = PlayerStats.objects.all()
    serializer_class = PlayerStatsSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['team', 'match']
    search_fields = ['name']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PlayerStatsDetailSerializer
        return PlayerStatsSerializer
    
    @action(detail=False)
    def top_performers(self, request):
        try:
            top_players = self.queryset.values('name', 'team__name')\
                .annotate(
                    total_goals=Sum('goals'),
                    total_assists=Sum('assists'),
                    avg_minutes=Avg('minutes_played')
                ).order_by('-total_goals')[:10]
            return Response(top_players)
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    
    def get_queryset(self):
        queryset = Player.objects.all()
        team_id = self.request.query_params.get('team', None)
        position = self.request.query_params.get('position', None)
        
        if team_id is not None:
            queryset = queryset.filter(team_id=team_id)
        if position is not None:
            queryset = queryset.filter(position=position)
            
        return queryset.select_related('team')

class MatchPredictionViewSet(viewsets.ModelViewSet):
    queryset = MatchPrediction.objects.all()
    serializer_class = MatchPredictionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['match']

class TeamFormationViewSet(viewsets.ModelViewSet):
    queryset = TeamFormation.objects.all()
    serializer_class = TeamFormationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['match', 'team']

class BettingOddsViewSet(viewsets.ModelViewSet):
    queryset = BettingOdds.objects.all()
    serializer_class = BettingOddsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['match']

class TopScorerViewSet(viewsets.ModelViewSet):
    queryset = TopScorer.objects.all()
    serializer_class = TopScorerSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['competition', 'team', 'season']
    search_fields = ['player_name']
    
    @action(detail=False)
    def season_leaders(self, request):
        try:
            season = request.query_params.get('season', None)
            competition = request.query_params.get('competition', None)
            
            queryset = self.queryset
            if season:
                queryset = queryset.filter(season=season)
            if competition:
                queryset = queryset.filter(competition=competition)
                
            leaders = queryset.order_by('-goals', '-assists')[:10]
            return Response(TopScorerSerializer(leaders, many=True).data)
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

from rest_framework.decorators import api_view

@api_view(['GET'])
def dashboard_stats(request):
    """
    Get aggregated dashboard statistics
    """
    try:
        total_matches = Match.objects.count()
        total_teams = Team.objects.count()
        total_players = Player.objects.count()

        return Response({
            'totalMatches': total_matches,
            'totalTeams': total_teams,
            'totalPlayers': total_players,
        })
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def dashboard_upcoming_matches(request):
    """
    Get upcoming matches for dashboard
    """
    try:
        upcoming_matches = Match.objects.filter(
            status='SCHEDULED'
        ).select_related(
            'home_team',
            'away_team',
            'competition'
        ).order_by('match_date')[:5]

        matches_data = [{
            'id': match.id,
            'homeTeam': match.home_team.name,
            'awayTeam': match.away_team.name,
            'date': match.match_date,
            'competition': match.competition.name,
        } for match in upcoming_matches]

        return Response({
            'upcomingMatches': matches_data
        })
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def dashboard_top_scorers(request):
    """
    Get top scorers for dashboard
    """
    try:
        top_scorers = PlayerStats.objects.select_related(
            'team'
        ).order_by('-goals')[:5]

        scorers_data = [{
            'playerId': stats.player_id,
            'playerName': stats.name,
            'team': stats.team.name,
            'goals': stats.goals,
        } for stats in top_scorers]

        return Response({
            'topScorers': scorers_data
        })
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
