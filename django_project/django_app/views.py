from django.db.models import Sum, Count, Avg, F, Q, Case, When
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from .models import Team, Competition, Match, TopScorer, Player, Area
from .serializers import (
    TeamSerializer,
    CompetitionSerializer,
    MatchSerializer,
    TopScorerSerializer,
    PlayerSerializer,
    TeamAnalyticsSerializer,
    CompetitionAnalyticsSerializer,
    MatchAnalyticsSerializer,
    PlayerAnalyticsSerializer
)
from django.db import connection
from django.db import models

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
            matches = Match.objects.all().order_by('-match_date')
            
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
            
            # Serialize the paginated data
            serializer = MatchSerializer(paginated_matches, many=True)
            
            # Return paginated response
            return paginator.get_paginated_response(serializer.data)
            
        except Exception as e:
            return Response({'error': str(e)}, status=500)

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
    def get(self, request):
        try:
            # Get all matches
            matches = Match.objects.all()
            total_matches = matches.count()
            total_goals = sum(match.home_team_score + match.away_team_score for match in matches)
            
            # Calculate goals trend
            goals_trend = self.calculate_goals_trend(matches)
            
            # Calculate area statistics
            teams = Team.objects.all()
            total_teams = teams.count()  # Get total number of teams
            area_stats = []
            area_counts = {}
            
            for team in teams:
                area = team.area
                if area in area_counts:
                    area_counts[area] += 1
                else:
                    area_counts[area] = 1
            
            for area, count in area_counts.items():
                area_stats.append({
                    'name': area,
                    'team_count': count
                })
            
            # Sort area_stats by team_count in descending order
            area_stats = sorted(area_stats, key=lambda x: x['team_count'], reverse=True)
            
            return Response({
                'summary': {
                    'total_matches': total_matches,
                    'total_goals': total_goals,
                    'average_goals_per_match': round(total_goals / total_matches, 2) if total_matches > 0 else 0,
                    'total_teams': total_teams  # Add total teams to the response
                },
                'goals_trend': goals_trend,
                'area_stats': area_stats
            })
        except Exception as e:
            return Response({'error': str(e)}, status=500)

class TeamAnalyticsView(APIView):
    def get(self, request, team_id):
        try:
            team = Team.objects.get(id=team_id)
            
            # Get match results
            matches = Match.objects.filter(
                Q(home_team=team) | Q(away_team=team),
                status='FINISHED'
            ).order_by('match_date')
            
            # Calculate performance metrics
            performance = []
            running_points = 0
            match_count = 0
            
            for match in matches:
                match_count += 1
                is_home = match.home_team_id == team.id
                team_score = match.home_team_score if is_home else match.away_team_score
                opponent_score = match.away_team_score if is_home else match.home_team_score
                
                # Calculate points for this match
                if team_score > opponent_score:
                    points = 3
                elif team_score == opponent_score:
                    points = 1
                else:
                    points = 0
                    
                running_points += points
                
                performance.append({
                    'match_date': match.match_date,
                    'opponent': match.away_team.name if is_home else match.home_team.name,
                    'score': f"{team_score}-{opponent_score}",
                    'points': points,
                    'running_points': running_points,
                    'average_points': round(running_points / match_count, 2)
                })
            
            # Get top scorers for the team
            top_scorers = TopScorer.objects.filter(team=team).order_by('-goals')[:5]
            
            return Response({
                'team_info': {
                    'name': team.name,
                    'founded': team.founded,
                    'venue': team.venue,
                    'area': team.area.name if team.area else 'Unknown'
                },
                'performance': performance,
                'top_scorers': [{
                    'player': scorer.player.name,
                    'goals': scorer.goals,
                    'assists': scorer.assists
                } for scorer in top_scorers]
            })
        except Team.DoesNotExist:
            return Response(
                {'error': 'Team not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"Error in TeamAnalyticsView: {str(e)}")
            return Response(
                {'error': 'Failed to fetch team analytics'},
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