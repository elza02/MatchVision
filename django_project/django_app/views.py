# Django imports
from django.db.models import (
    Q, F, Count, Avg, Sum, Case, When, FloatField,
    ExpressionWrapper, Value
)
from django.db.models.functions import Cast, Coalesce
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction

# Rest Framework imports
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

# Third-party imports
from django_filters.rest_framework import DjangoFilterBackend

# Local imports
from .models import (
    Team, Competition, Match, PlayerStats, Player,
    MatchPrediction, TeamFormation, BettingOdds, TopScorer
)
from .serializers import (
    TeamSerializer, CompetitionSerializer, MatchSerializer,
    PlayerStatsSerializer, MatchPredictionSerializer,
    TeamDetailSerializer, MatchDetailSerializer, PlayerStatsDetailSerializer,
    PlayerSerializer,
    TeamFormationSerializer,
    BettingOddsSerializer, TopScorerSerializer
)

# Logging setup
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
    def statistics(self, request, pk=None):
        """Get comprehensive statistics for a competition"""
        logger.info(f"Fetching statistics for competition ID: {pk}")
        try:
            # Try to get the competition or return 404
            try:
                competition = Competition.objects.get(pk=pk)
                logger.info(f"Found competition: {competition.name}")
            except Competition.DoesNotExist:
                logger.warning(f"Competition with ID {pk} not found")
                return Response(
                    {"error": f"Competition with ID {pk} not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get all matches for this competition
            matches = Match.objects.filter(competition=competition)
            logger.info(f"Found {matches.count()} matches for competition")
            
            # If no matches found, return empty stats
            if not matches.exists():
                logger.info("No matches found, returning empty stats")
                return Response({
                    'overall': {
                        'totalMatches': 0,
                        'totalGoals': 0,
                        'averageGoalsPerMatch': 0,
                        'homeWins': 0,
                        'awayWins': 0,
                        'draws': 0
                    },
                    'teams': [],
                    'topScorers': []
                })
            
            try:
                # Overall statistics
                logger.info("Calculating overall statistics")
                overall_stats = matches.aggregate(
                    total_matches=Count('id'),
                    total_goals=Coalesce(Sum(F('home_team_score')), 0) + Coalesce(Sum(F('away_team_score')), 0),
                    home_wins=Count('id', filter=Q(home_team_score__gt=F('away_team_score'))),
                    away_wins=Count('id', filter=Q(away_team_score__gt=F('home_team_score'))),
                    draws=Count('id', filter=Q(home_team_score=F('away_team_score')))
                )
                
                # Calculate average goals per match
                total_matches = overall_stats['total_matches']
                total_goals = overall_stats['total_goals']
                avg_goals = round(total_goals / total_matches, 2) if total_matches > 0 else 0
                
                logger.info("Successfully calculated overall statistics")
                
                return Response({
                    'overall': {
                        'totalMatches': total_matches,
                        'totalGoals': total_goals,
                        'averageGoalsPerMatch': avg_goals,
                        'homeWins': overall_stats['home_wins'],
                        'awayWins': overall_stats['away_wins'],
                        'draws': overall_stats['draws']
                    },
                    'teams': [],  # Simplified for debugging
                    'topScorers': []  # Simplified for debugging
                })
            
            except Exception as calc_error:
                logger.error(f"Error calculating statistics: {str(calc_error)}")
                raise calc_error
                
        except Exception as e:
            logger.error(f"Error in competition statistics for ID {pk}: {str(e)}")
            return Response(
                {"error": f"An error occurred while fetching statistics: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
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
        """Helper method to get team's form from recent matches"""
        form = []
        for match in recent_matches:
            if match.home_team == team:
                if match.home_team_score > match.away_team_score:
                    form.append('W')
                elif match.home_team_score < match.away_team_score:
                    form.append('L')
                else:
                    form.append('D')
            else:  # Away team
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
            top_scorers = PlayerStats.objects.filter(
                match__competition=competition
            ).values(
                'player_id',
                'name',
                'team__name'
            ).annotate(
                total_goals=Sum('goals'),
                total_assists=Sum('assists'),
                matches_played=Count('match', distinct=True)
            ).filter(
                total_goals__gt=0
            ).order_by('-total_goals')[:5]
            
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
    filterset_fields = ['competition', 'status', 'season']
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

# class TwitterFeedViewSet(viewsets.ViewSet):
#     def list(self, request):
#         """
#         Get football-related tweets based on query parameters
#         """
#         try:
#             client = get_twitter_client()
#             if not client:
#                 return Response(
#                     {"error": "Twitter client configuration error"},
#                     status=status.HTTP_503_SERVICE_UNAVAILABLE
#                 )

#             # Get query parameters
#             query = request.query_params.get('query', '')
#             category = request.query_params.get('category', '')
#             max_results = min(int(request.query_params.get('max_results', 10)), 10)

#             # Build search query with football-specific terms
#             search_terms = [
#                 'football', 'soccer', 'FIFA', 'UEFA',
#                 'premier league', 'laliga', 'bundesliga', 'serie a', 'ligue 1',
#                 'champions league', 'europa league',
#                 'goal', 'match', 'transfer'
#             ]

#             # Add category-specific terms
#             if category:
#                 if category == "Transfer News":
#                     search_terms.extend(['transfer', 'sign', 'deal', 'contract', 'bid'])
#                 elif category == "Match Updates":
#                     search_terms.extend(['score', 'goal', 'match', 'game', 'lineup'])
#                 elif category == "Player Stats":
#                     search_terms.extend(['stats', 'performance', 'rating', 'assist'])
#                 elif category == "Team News":
#                     search_terms.extend(['team', 'club', 'squad', 'injury', 'training'])
#                 elif category == "Injuries":
#                     search_terms.extend(['injury', 'injured', 'recovery', 'fitness'])
#                 elif category == "Highlights":
#                     search_terms.extend(['highlight', 'goal', 'save', 'skill'])
#                 elif category == "Analysis":
#                     search_terms.extend(['analysis', 'tactics', 'performance', 'stats'])
#                 elif category == "Predictions":
#                     search_terms.extend(['prediction', 'odds', 'preview', 'forecast'])

#             # Build the search query
#             base_query = query if query else ' OR '.join(search_terms[:3])  # Use first 3 terms as default
#             search_query = f"({base_query})"

#             # Add language and filter parameters
#             search_query += " lang:en -is:retweet"
            
#             # Add engagement filters to get higher quality tweets
#             search_query += " min_faves:10"  # Tweets with at least 10 likes

#             # Get tweets with rate limiting
#             tweets = safe_twitter_request(
#                 'search_tweets',
#                 client.search_recent_tweets,
#                 query=search_query,
#                 max_results=max_results,
#                 tweet_fields=['created_at', 'public_metrics', 'entities', 'context_annotations'],
#                 expansions=['author_id'],
#                 user_fields=['username', 'name', 'profile_image_url']
#             )

#             if not tweets or not tweets.data:
#                 return Response({"results": []})

#             # Create user lookup dictionary
#             users = {user.id: user for user in tweets.includes['users']} if 'users' in tweets.includes else {}

#             # Format tweets with enhanced information
#             formatted_tweets = []
#             for tweet in tweets.data:
#                 # Get user information
#                 author = users.get(tweet.author_id, {})
                
#                 # Check if tweet has football-related context
#                 is_football_related = False
#                 if hasattr(tweet, 'context_annotations'):
#                     for context in tweet.context_annotations:
#                         if any(term in context.entity.name.lower() for term in ['sport', 'football', 'soccer']):
#                             is_football_related = True
#                             break

#                 # Only include football-related tweets
#                 if is_football_related or any(term.lower() in tweet.text.lower() for term in search_terms):
#                     tweet_data = {
#                         'id': tweet.id,
#                         'text': tweet.text,
#                         'created_at': tweet.created_at,
#                         'metrics': tweet.public_metrics,
#                         'hashtags': [tag['tag'] for tag in tweet.entities['hashtags']] if tweet.entities and 'hashtags' in tweet.entities else [],
#                         'author': {
#                             'id': author.id if author else None,
#                             'username': author.username if author else None,
#                             'name': author.name if author else None,
#                             'profile_image_url': author.profile_image_url if author else None
#                         }
#                     }
#                     formatted_tweets.append(tweet_data)

#             return Response({
#                 "results": formatted_tweets,
#                 "meta": {
#                     "result_count": len(formatted_tweets),
#                     "newest_id": tweets.meta.get("newest_id"),
#                     "oldest_id": tweets.meta.get("oldest_id"),
#                     "search_query": search_query  # Include the search query for debugging
#                 }
#             })

#         except Exception as e:
#             return Response(
#                 {"error": str(e)},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )

#     @action(detail=False, methods=['get'])
#     def categories(self, request):
#         """
#         Get predefined tweet categories
#         """
#         categories = [
#             "Transfer News",
#             "Match Updates",
#             "Player Stats",
#             "Team News",
#             "Injuries",
#             "Highlights",
#             "Analysis",
#             "Predictions"
#         ]
#         return Response({"results": categories})

#     @action(detail=False, methods=['get'])
#     def trending(self, request):
#         """
#         Get trending football topics
#         """
#         try:
#             api = get_twitter_api()
#             if not api:
#                 return Response(
#                     {"error": "Twitter API configuration error"},
#                     status=status.HTTP_503_SERVICE_UNAVAILABLE
#                 )

#             # Get worldwide trends with rate limiting
#             trends = safe_twitter_request(
#                 'get_trends',
#                 api.get_place_trends,
#                 1  # 1 is the woeid for worldwide
#             )
            
#             # Filter football-related trends
#             football_terms = ['football', 'soccer', 'goal', 'match', 'player', 'team', 
#                             'league', 'cup', 'transfer', 'stadium', 'coach', 'manager']
            
#             football_trends = []
#             for trend in trends[0]['trends']:
#                 trend_name = trend['name'].lower()
#                 if any(term in trend_name for term in football_terms):
#                     football_trends.append({
#                         'name': trend['name'],
#                         'url': trend['url'],
#                         'tweet_volume': trend['tweet_volume']
#                     })

#             return Response({
#                 "results": football_trends[:10],  # Return top 10 football trends
#                 "meta": {
#                     "result_count": len(football_trends[:10]),
#                     "timestamp": trends[0]['created_at'] if trends[0].get('created_at') else None
#                 }
#             })

#         except Exception as e:
#             return Response(
#                 {"error": str(e)},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )

class AnalyticsViewSet(viewsets.ViewSet):
    def get_competition_analytics(self, request, competition_id):
        """Get analytics data for a specific competition"""
        try:
            # First check if competition exists
            try:
                competition = Competition.objects.get(id=competition_id)
            except Competition.DoesNotExist:
                return Response(
                    {"error": f"Competition with ID {competition_id} not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Get matches for the competition with related teams
            matches = list(Match.objects.filter(
                competition=competition
            ).select_related(
                'home_team', 'away_team'
            ).order_by('-match_date')[:10])

            if not matches:
                return Response({
                    "match_analytics": [],
                    "top_scorers": [],
                    "standings": [],
                    "message": f"No matches found for competition {competition.name}"
                })

            # Get teams in the competition
            team_ids = set()
            for match in matches:
                team_ids.add(match.home_team_id)
                team_ids.add(match.away_team_id)
            teams = Team.objects.filter(id__in=team_ids)

            # Get players in these teams
            players = Player.objects.filter(team__in=teams).select_related('team')

            # Calculate match analytics
            match_analytics = []
            for match in matches:
                match_analytics.append({
                    'match_date': match.match_date,
                    'home_team': match.home_team.name,
                    'away_team': match.away_team.name,
                    'home_team_score': match.home_team_score or 0,
                    'away_team_score': match.away_team_score or 0,
                    'total_goals': (match.home_team_score or 0) + (match.away_team_score or 0),
                    'winner': match.home_team.name if match.home_team_score > match.away_team_score 
                            else match.away_team.name if match.away_team_score > match.home_team_score 
                            else 'Draw'
                })

            # Calculate top scorers using annotations
            top_scorers = []
            for player in players:
                goals_count = Goal.objects.filter(scorer=player, match__in=matches).count()
                assists_count = Goal.objects.filter(assistant=player, match__in=matches).count()
                
                if goals_count > 0 or assists_count > 0:
                    top_scorers.append({
                        'player_id': player.id,
                        'player_name': player.name,
                        'team': player.team.name,
                        'goals': goals_count,
                        'assists': assists_count
                    })

            # Sort by goals, then assists
            top_scorers.sort(key=lambda x: (x['goals'], x['assists']), reverse=True)

            # Calculate team standings
            standings = []
            for team in teams:
                # Initialize counters
                won = draw = lost = goals_for = goals_against = 0
                
                # Calculate stats from matches list
                team_matches = [m for m in matches if m.home_team_id == team.id or m.away_team_id == team.id]
                
                for match in team_matches:
                    if match.home_team_id == team.id:
                        goals_for += match.home_team_score or 0
                        goals_against += match.away_team_score or 0
                        if match.home_team_score > match.away_team_score:
                            won += 1
                        elif match.home_team_score < match.away_team_score:
                            lost += 1
                        else:
                            draw += 1
                    else:  # away team
                        goals_for += match.away_team_score or 0
                        goals_against += match.home_team_score or 0
                        if match.away_team_score > match.home_team_score:
                            won += 1
                        elif match.away_team_score < match.home_team_score:
                            lost += 1
                        else:
                            draw += 1

                matches_played = won + draw + lost
                points = won * 3 + draw
                goal_difference = goals_for - goals_against

                if matches_played > 0:
                    standings.append({
                        'team_id': team.id,
                        'team_name': team.name,
                        'matches_played': matches_played,
                        'won': won,
                        'drawn': draw,
                        'lost': lost,
                        'goals_for': goals_for,
                        'goals_against': goals_against,
                        'goal_difference': goal_difference,
                        'points': points,
                    })

            # Sort standings by points, then goal difference
            standings.sort(key=lambda x: (x['points'], x['goal_difference']), reverse=True)

            return Response({
                'competition': {
                    'id': competition.id,
                    'name': competition.name,
                    'area': competition.area
                },
                'match_analytics': match_analytics,
                'top_scorers': top_scorers[:10],  # Top 10 scorers
                'standings': standings
            })

        except Exception as e:
            logger.error(f"Error in get_competition_analytics for competition {competition_id}: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_team_analytics(self, request, team_id):
        """Get analytics data for a specific team"""
        try:
            team = Team.objects.get(id=team_id)
            matches = Match.objects.filter(Q(home_team=team) | Q(away_team=team)).order_by('-match_date')[:10]
            
            match_analytics = []
            for match in matches:
                is_home = match.home_team == team
                match_analytics.append({
                    'match_date': match.match_date,
                    'opponent': match.away_team.name if is_home else match.home_team.name,
                    'goals_scored': match.home_team_score if is_home else match.away_team_score,
                    'goals_conceded': match.away_team_score if is_home else match.home_team_score,
                    'result': 'W' if (is_home and match.home_team_score > match.away_team_score) or
                                   (not is_home and match.away_team_score > match.home_team_score)
                             else 'L' if (is_home and match.home_team_score < match.away_team_score) or
                                       (not is_home and match.away_team_score < match.home_team_score)
                             else 'D'
                })
            
            return Response({
                'team_name': team.name,
                'match_analytics': match_analytics
            })
            
        except Team.DoesNotExist:
            return Response(
                {'error': 'Team not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error in get_team_analytics for team {team_id}: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_player_analytics(self, request, player_id):
        """Get analytics data for a specific player"""
        try:
            player = Player.objects.get(id=player_id)
            goals = Goal.objects.filter(scorer=player)
            assists = Goal.objects.filter(assistant=player)
            
            matches_played = Match.objects.filter(
                Q(home_team=player.team) | Q(away_team=player.team)
            ).count()
            
            return Response({
                'player_name': player.name,
                'team': player.team.name,
                'matches_played': matches_played,
                'goals': goals.count(),
                'assists': assists.count(),
                'goals_per_match': round(goals.count() / matches_played if matches_played > 0 else 0, 2)
            })
            
        except Player.DoesNotExist:
            return Response(
                {'error': 'Player not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error in get_player_analytics for player {player_id}: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

def get_team_form(team, matches_count=5):
    """Helper function to get team's recent form"""
    recent_matches = Match.objects.filter(
        Q(home_team=team) | Q(away_team=team),
        status='FINISHED'
    ).order_by('-match_date')[:matches_count]
    
    form = []
    for match in recent_matches:
        if match.home_team == team:
            if match.home_team_score > match.away_team_score:
                form.append('W')
            elif match.home_team_score < match.away_team_score:
                form.append('L')
            else:
                form.append('D')
        else:  # Away team
            if match.away_team_score > match.home_team_score:
                form.append('W')
            elif match.away_team_score < match.home_team_score:
                form.append('L')
            else:
                form.append('D')
    return form

@api_view(['GET'])
def dashboard_stats(request):
    """Get aggregated dashboard statistics with enhanced metrics"""
    try:
        # Basic counts with proper null handling
        total_matches = Match.objects.count()
        total_teams = Team.objects.count()
        total_players = Player.objects.count()
        
        # Recent match statistics
        recent_matches = Match.objects.filter(
            status='FINISHED'
        ).order_by('-match_date')[:10]
        
        avg_goals = recent_matches.aggregate(
            avg_goals=Coalesce(
                ExpressionWrapper(
                    (Avg('home_team_score') + Avg('away_team_score')) / 2,
                    output_field=FloatField()
                ),
                0
            )
        )['avg_goals']
        
        # League performance metrics
        league_stats = Competition.objects.annotate(
            match_count=Count('match'),
            avg_goals=Coalesce(
                ExpressionWrapper(
                    Avg(F('match__home_team_score') + F('match__away_team_score')),
                    output_field=FloatField()
                ),
                0
            ),
            total_teams=Count('match__home_team', distinct=True)
        ).filter(
            match_count__gt=0
        ).order_by('-match_count')[:5]
        
        # Team form analysis
        team_forms = Team.objects.annotate(
            recent_wins=Count(
                'home_matches',
                filter=Q(
                    home_matches__status='FINISHED',
                    home_matches__home_team_score__gt=F('home_matches__away_team_score')
                )
            ) + Count(
                'away_matches',
                filter=Q(
                    away_matches__status='FINISHED',
                    away_matches__away_team_score__gt=F('away_matches__home_team_score')
                )
            )
        ).order_by('-recent_wins')[:5]
        
        return Response({
            'overview': {
                'totalMatches': total_matches,
                'totalTeams': total_teams,
                'totalPlayers': total_players,
                'averageGoalsPerMatch': round(float(avg_goals), 2) if avg_goals else 0
            },
            'leaguePerformance': [{
                'name': comp.name,
                'matchCount': comp.match_count,
                'averageGoals': round(float(comp.avg_goals), 2),
                'totalTeams': comp.total_teams
            } for comp in league_stats],
            'topTeams': [{
                'name': team.name,
                'recentWins': team.recent_wins,
                'crest': team.crest
            } for team in team_forms],
        })
    except Exception as e:
        logger.error(f"Error in dashboard_stats: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def dashboard_upcoming_matches(request):
    """Get upcoming matches for dashboard with enhanced match details"""
    try:
        upcoming_matches = Match.objects.filter(
            status='SCHEDULED',
            match_date__gte=timezone.now()
        ).select_related(
            'home_team',
            'away_team',
            'competition'
        ).order_by('match_date')[:5]

        matches_data = []
        for match in upcoming_matches:
            # Get team forms
            home_form = get_team_form(match.home_team)
            away_form = get_team_form(match.away_team)
            
            # Get head-to-head history
            h2h = Match.objects.filter(
                status='FINISHED'
            ).filter(
                Q(
                    home_team=match.home_team,
                    away_team=match.away_team
                ) | Q(
                    home_team=match.away_team,
                    away_team=match.home_team
                )
            ).order_by('-match_date')[:5]
            
            h2h_summary = {
                'home_wins': sum(1 for m in h2h if 
                    (m.home_team == match.home_team and m.home_team_score > m.away_team_score) or
                    (m.away_team == match.home_team and m.away_team_score > m.home_team_score)
                ),
                'away_wins': sum(1 for m in h2h if 
                    (m.home_team == match.away_team and m.home_team_score > m.away_team_score) or
                    (m.away_team == match.away_team and m.away_team_score > m.home_team_score)
                ),
                'draws': sum(1 for m in h2h if m.home_team_score == m.away_team_score)
            }
            
            matches_data.append({
                'id': match.id,
                'homeTeam': {
                    'name': match.home_team.name,
                    'crest': match.home_team.crest,
                    'form': home_form
                },
                'awayTeam': {
                    'name': match.away_team.name,
                    'crest': match.away_team.crest,
                    'form': away_form
                },
                'date': match.match_date,
                'competition': {
                    'name': match.competition.name,
                    'code': match.competition.code
                },
                'headToHead': h2h_summary
            })

        return Response({
            'upcomingMatches': matches_data
        })
    except Exception as e:
        logger.error(f"Error in dashboard_upcoming_matches: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def dashboard_top_scorers(request):
    """Get top scorers for dashboard with enhanced player statistics"""
    try:
        top_scorers = PlayerStats.objects.values(
            'player_id',
            'name',
            'team__name',
            'team__crest'
        ).annotate(
            total_goals=Sum('goals'),
            total_assists=Sum('assists'),
            matches_played=Count('match_id', distinct=True)
        ).annotate(
            goals_per_match=ExpressionWrapper(
                Cast('total_goals', FloatField()) / Cast('matches_played', FloatField()),
                output_field=FloatField()
            ),
            minutes_per_goal=Case(
                When(total_goals__gt=0, 
                     then=Cast(Sum('minutes_played'), FloatField()) / Cast('total_goals', FloatField())),
                default=None,
                output_field=FloatField()
            )
        ).filter(
            total_goals__gt=0
        ).order_by('-total_goals')[:10]

        scorers_data = [{
            'playerId': scorer['player_id'],
            'playerName': scorer['name'],
            'team': scorer['team__name'],
            'teamCrest': scorer['team__crest'],
            'stats': {
                'goals': scorer['total_goals'],
                'assists': scorer['total_assists'],
                'matchesPlayed': scorer['matches_played'],
                'goalsPerMatch': round(scorer['goals_per_match'], 2) if scorer['goals_per_match'] else 0,
                'minutesPerGoal': round(scorer['minutes_per_goal'], 2) if scorer['minutes_per_goal'] else None
            }
        } for scorer in top_scorers]

        return Response({
            'topScorers': scorers_data
        })
    except Exception as e:
        logger.error(f"Error in dashboard_top_scorers: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
