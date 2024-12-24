from django.db.models import Sum, Count, Avg, F, Q, Case, When
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from .models import Team, Competition, Match, TopScorer, Player, Area, Standing
from .serializers import (
    TeamSerializer,
    CompetitionSerializer,
    MatchSerializer,
    TopScorerSerializer,
    PlayerSerializer,
    TeamAnalyticsSerializer,
    CompetitionAnalyticsSerializer,
    MatchAnalyticsSerializer,
    PlayerAnalyticsSerializer,
    StandingSerializer
)
from django.db import connection
from django.db import models
from django.shortcuts import get_object_or_404

class DashboardStatsView(APIView):
    def get(self, request):
        try:
            # Get total counts only
            total_teams = Team.objects.count()
            total_matches = Match.objects.count()
            total_players = Player.objects.count()

            response_data = {
                "total_teams": total_teams,
                "total_matches": total_matches,
                "total_players": total_players
            }

            print("Stats response data:", response_data)
            return Response(response_data)
        except Exception as e:
            print(f"Error in DashboardStatsView: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class DashboardMatchesView(APIView):
    def get(self, request):
        try:
            recent_matches = Match.objects.select_related(
                'home_team', 'away_team', 'competition'
            ).order_by('-match_date')[:5]

            response_data = MatchSerializer(recent_matches, many=True).data
            print(f"Matches response data: {len(response_data)} matches")
            return Response(response_data)
        except Exception as e:
            print(f"Error in DashboardMatchesView: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class DashboardScorersView(APIView):
    def get(self, request):
        try:
            top_scorers = TopScorer.objects.select_related(
                'player', 'player__team', 'competition'
            ).filter(
                player__isnull=False,
                goals__gt=0
            ).order_by('-goals')[:10]

            response_data = TopScorerSerializer(top_scorers, many=True).data
            print(f"Scorers response data: {len(response_data)} scorers")
            return Response(response_data)
        except Exception as e:
            print(f"Error in DashboardScorersView: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class MatchPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class MatchListView(APIView):
    pagination_class = MatchPagination

    def get(self, request):
        try:
            # Get query parameters
            status = request.query_params.get('status')
            competition = request.query_params.get('competition')
            team = request.query_params.get('team')
            date_from = request.query_params.get('date_from')
            date_to = request.query_params.get('date_to')
            
            # Start with all matches
            matches = Match.objects.select_related(
                'competition', 'home_team', 'away_team'
            ).order_by('-match_date')
            
            # Apply filters
            if status:
                matches = matches.filter(status=status)
            if competition:
                matches = matches.filter(competition_id=competition)
            if team:
                matches = matches.filter(Q(home_team_id=team) | Q(away_team_id=team))
            if date_from:
                matches = matches.filter(match_date__gte=date_from)
            if date_to:
                matches = matches.filter(match_date__lte=date_to)

            # Get paginator
            paginator = self.pagination_class()
            paginated_matches = paginator.paginate_queryset(matches, request)
            
            if paginated_matches is None:
                return Response({
                    'error': 'Invalid page number',
                    'message': 'The requested page number is out of range.'
                }, status=400)
            
            # Serialize the paginated data
            serializer = MatchSerializer(paginated_matches, many=True)
            
            # Return paginated response
            return paginator.get_paginated_response(serializer.data)
            
        except Exception as e:
            print(f"Error in MatchListView: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class MatchDetailView(generics.RetrieveAPIView):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer

class TeamPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })

class TeamListView(APIView):
    pagination_class = TeamPagination

    def get(self, request):
        try:
            # Get query parameters
            area = request.query_params.get('area')
            search = request.query_params.get('search')
            
            # Start with teams that have actual data
            teams = Team.objects.select_related('area').filter(
                Q(name__isnull=False) | 
                Q(short_name__isnull=False) |
                Q(tla__isnull=False)
            )
            
            # Debug: Print raw SQL and first few records
            from django.db import connection
            print("\nDEBUG: Executing raw SQL query:")
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT t.id, t.name, t.short_name, t.tla, t.crest, t.venue, t.founded, 
                           a.id as area_id, a.name as area_name 
                    FROM teams t 
                    LEFT JOIN areas a ON t.area_id = a.id 
                    WHERE t.name IS NOT NULL 
                       OR t.short_name IS NOT NULL 
                       OR t.tla IS NOT NULL
                    ORDER BY t.name 
                    LIMIT 5
                """)
                columns = [col[0] for col in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]
                print("Raw Database Results:")
                for row in results:
                    print(row)
            
            # Apply filters
            if area:
                teams = teams.filter(area_id=area)
            if search:
                teams = teams.filter(
                    Q(name__icontains=search) |
                    Q(short_name__icontains=search) |
                    Q(tla__icontains=search)
                )

            # Apply ordering - prioritize teams with names
            teams = teams.order_by(
                models.F('name').asc(nulls_last=True),
                models.F('short_name').asc(nulls_last=True)
            )

            # Get paginator
            paginator = self.pagination_class()
            paginated_teams = paginator.paginate_queryset(teams, request)
            
            # Serialize and return the data
            serializer = TeamSerializer(paginated_teams, many=True)
            return paginator.get_paginated_response(serializer.data)
            
        except Exception as e:
            print(f"Error in TeamListView: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response(
                {'error': 'Failed to fetch teams. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class TeamDetailView(generics.RetrieveAPIView):
    queryset = Team.objects.select_related('area').all()
    serializer_class = TeamSerializer

class PlayerListView(generics.ListAPIView):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer

class PlayerDetailView(generics.RetrieveAPIView):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer

class CompetitionListView(generics.ListAPIView):
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer

class CompetitionDetailView(generics.RetrieveAPIView):
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer

class MatchPredictionsView(APIView):
    def get(self, request):
        match_id = request.query_params.get('match_id')
        # Mocked predictions; replace with actual logic
        predictions = {
            "match_id": match_id,
            "home_win_probability": 0.45,
            "draw_probability": 0.30,
            "away_win_probability": 0.25,
        }
        return Response(predictions)

class AnalyticsOverviewView(APIView):
    def calculate_goals_trend(self, matches):
        goals_trend = []
        try:
            if matches:
                matches = matches.order_by('match_date')
                running_total = 0
                match_count = 0
                
                for match in matches:
                    if match.match_date:  # Only include matches with valid dates
                        match_count += 1
                        match_goals = (match.home_team_score or 0) + (match.away_team_score or 0)
                        running_total += match_goals
                        goals_trend.append({
                            'matchday': match_count,
                            'average_goals': round(running_total / match_count, 2),
                            'date': match.match_date.strftime('%Y-%m-%d')
                        })
        except Exception as e:
            print(f"Error calculating goals trend: {str(e)}")
            return []
        return goals_trend

    def get(self, request):
        try:
            # Get all matches with status check
            matches = Match.objects.filter(status='FINISHED')
            if not matches.exists():
                return Response({
                    'summary': {
                        'total_matches': 0,
                        'total_goals': 0,
                        'average_goals_per_match': 0,
                        'total_teams': 0
                    },
                    'goals_trend': [],
                    'area_stats': []
                })

            total_matches = matches.count()
            
            # Calculate total goals safely handling None values
            total_goals = sum(
                (match.home_team_score or 0) + (match.away_team_score or 0) 
                for match in matches
            )
            
            # Calculate goals trend
            goals_trend = self.calculate_goals_trend(matches)
            
            # Calculate area statistics
            teams = Team.objects.all()
            total_teams = teams.count()
            area_counts = {}
            
            for team in teams:
                area_name = team.area.name if team.area else "Unknown"  # Get area name directly
                area_counts[area_name] = area_counts.get(area_name, 0) + 1
            
            area_stats = [
                {
                    'name': area_name,
                    'team_count': count
                }
                for area_name, count in area_counts.items()
                if area_name  # Filter out any remaining None values
            ]
            
            # Sort area_stats by team_count in descending order
            area_stats = sorted(area_stats, key=lambda x: x['team_count'], reverse=True)
            
            response_data = {
                'summary': {
                    'total_matches': total_matches,
                    'total_goals': total_goals,
                    'average_goals_per_match': round(total_goals / total_matches, 2) if total_matches > 0 else 0,
                    'total_teams': total_teams
                },
                'goals_trend': goals_trend,
                'area_stats': area_stats
            }
            
            return Response(response_data)
            
        except Exception as e:
            print(f"Error in AnalyticsOverviewView: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class TeamAnalyticsView(APIView):
    def get(self, request, team_id):
        try:
            print(f"\n=== TeamAnalyticsView ===")
            print(f"Request method: {request.method}")
            print(f"Request path: {request.path}")
            print(f"Team ID: {team_id}")
            
            # Verify team exists
            team = get_object_or_404(Team, id=team_id)
            print(f"Found team: {team.name} (ID: {team.id})")
            
            # Get team's matches
            matches = Match.objects.filter(
                Q(home_team=team) | Q(away_team=team),
                status='FINISHED'
            ).order_by('match_date')
            
            match_count = matches.count()
            print(f"Found {match_count} matches for team")
            
            if not matches.exists():
                print("No matches found for team")
                response_data = {
                    'performance': [],
                    'summary': {
                        'total_matches': 0,
                        'wins': 0,
                        'draws': 0,
                        'losses': 0,
                        'goals_for': 0,
                        'goals_against': 0,
                        'goal_difference': 0,
                        'points': 0,
                        'average_points': 0
                    }
                }
                print("Returning empty response:", response_data)
                return Response(response_data)
            
            # Calculate performance metrics
            performance = []
            running_points = 0
            total_matches = 0
            wins = 0
            draws = 0
            losses = 0
            goals_for = 0
            goals_against = 0
            
            print("\nProcessing matches:")
            for match in matches:
                total_matches += 1
                
                # Determine if team was home or away
                is_home = match.home_team == team
                team_score = match.home_team_score if is_home else match.away_team_score
                opponent_score = match.away_team_score if is_home else match.home_team_score
                opponent = match.away_team if is_home else match.home_team
                
                # Handle None values
                team_score = team_score or 0
                opponent_score = opponent_score or 0
                
                print(f"Match {total_matches}: {team.name} vs {opponent.name} - Score: {team_score}-{opponent_score}")
                
                # Update statistics
                goals_for += team_score
                goals_against += opponent_score
                
                # Calculate match points
                if team_score > opponent_score:
                    points = 3
                    wins += 1
                    result = 'W'
                elif team_score == opponent_score:
                    points = 1
                    draws += 1
                    result = 'D'
                else:
                    points = 0
                    losses += 1
                    result = 'L'
                
                running_points += points
                
                match_data = {
                    'match_date': match.match_date.strftime('%Y-%m-%d'),
                    'opponent': opponent.name,
                    'score': f"{team_score}-{opponent_score}",
                    'result': result,
                    'points': points,
                    'running_points': running_points,
                    'average_points': round(running_points / total_matches, 2)
                }
                print(f"Match data: {match_data}")
                performance.append(match_data)
            
            response_data = {
                'performance': performance,
                'summary': {
                    'total_matches': total_matches,
                    'wins': wins,
                    'draws': draws,
                    'losses': losses,
                    'goals_for': goals_for,
                    'goals_against': goals_against,
                    'goal_difference': goals_for - goals_against,
                    'points': running_points,
                    'average_points': round(running_points / total_matches, 2) if total_matches > 0 else 0
                }
            }
            
            print("\nFinal response data:")
            print("Summary:", response_data['summary'])
            print(f"Performance entries: {len(response_data['performance'])}")
            
            return Response(response_data)
            
        except Team.DoesNotExist:
            print(f"Team {team_id} not found")
            return Response(
                {'error': 'Team not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"Error in TeamAnalyticsView: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CompetitionAnalyticsView(APIView):
    def get(self, request, competition_id):
        try:
            competition = Competition.objects.get(id=competition_id)
            serializer = CompetitionAnalyticsSerializer(competition)
            return Response(serializer.data)
        except Competition.DoesNotExist:
            return Response(
                {"error": "Competition not found"},
                status=status.HTTP_404_NOT_FOUND
            )

class MatchAnalyticsView(APIView):
    def get(self, request, match_id):
        try:
            match = Match.objects.get(id=match_id)
            serializer = MatchAnalyticsSerializer(match)
            return Response(serializer.data)
        except Match.DoesNotExist:
            return Response(
                {"error": "Match not found"},
                status=status.HTTP_404_NOT_FOUND
            )

class PlayerAnalyticsView(APIView):
    def get(self, request, player_id):
        try:
            player = Player.objects.get(id=player_id)
            serializer = PlayerAnalyticsSerializer(player)
            return Response(serializer.data)
        except Player.DoesNotExist:
            return Response(
                {"error": "Player not found"},
                status=status.HTTP_404_NOT_FOUND
            )

class TeamComparisonView(APIView):
    def get(self, request, team1_id, team2_id):
        try:
            team1 = Team.objects.get(id=team1_id)
            team2 = Team.objects.get(id=team2_id)
            
            # Head-to-head matches
            h2h_matches = Match.objects.filter(
                Q(home_team=team1, away_team=team2) |
                Q(home_team=team2, away_team=team1)
            ).order_by('-match_date')
            
            # Calculate head-to-head stats
            team1_wins = 0
            team2_wins = 0
            draws = 0
            
            for match in h2h_matches:
                if match.home_team_score > match.away_team_score:
                    if match.home_team == team1:
                        team1_wins += 1
                    else:
                        team2_wins += 1
                elif match.home_team_score < match.away_team_score:
                    if match.away_team == team1:
                        team1_wins += 1
                    else:
                        team2_wins += 1
                else:
                    draws += 1
            
            # Get recent form for both teams
            team1_form = TeamAnalyticsSerializer().get_form_analysis(team1)
            team2_form = TeamAnalyticsSerializer().get_form_analysis(team2)
            
            # Get top scorers for both teams
            team1_scorers = TopScorer.objects.filter(team=team1).order_by('-goals')[:5]
            team2_scorers = TopScorer.objects.filter(team=team2).order_by('-goals')[:5]
            
            return Response({
                'head_to_head': {
                    'total_matches': len(h2h_matches),
                    f'{team1.name}_wins': team1_wins,
                    f'{team2.name}_wins': team2_wins,
                    'draws': draws,
                    'recent_matches': MatchSerializer(h2h_matches[:5], many=True).data
                },
                'team_comparison': {
                    team1.name: {
                        'form': team1_form,
                        'top_scorers': [
                            {
                                'name': scorer.player.name,
                                'goals': scorer.goals,
                                'assists': scorer.assists
                            } for scorer in team1_scorers
                        ]
                    },
                    team2.name: {
                        'form': team2_form,
                        'top_scorers': [
                            {
                                'name': scorer.player.name,
                                'goals': scorer.goals,
                                'assists': scorer.assists
                            } for scorer in team2_scorers
                        ]
                    }
                }
            })
        except Team.DoesNotExist:
            return Response(
                {"error": "One or both teams not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class StandingListView(generics.ListAPIView):
    serializer_class = StandingSerializer
    
    def get_queryset(self):
        queryset = Standing.objects.select_related('team', 'competition', 'area').all()
        
        # Filter by competition if provided
        competition_id = self.request.query_params.get('competition', None)
        if competition_id:
            queryset = queryset.filter(competition_id=competition_id)
            
        # Filter by season if provided
        season = self.request.query_params.get('season', None)
        if season:
            queryset = queryset.filter(season=season)
            
        # Order by position by default
        return queryset.order_by('position')

class StandingDetailView(generics.RetrieveAPIView):
    queryset = Standing.objects.select_related('team', 'competition', 'area').all()
    serializer_class = StandingSerializer