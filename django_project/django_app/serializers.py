from rest_framework import serializers
from django.db.models import Count, Avg, Sum, F, Q
from .models import Team, Competition, Match, TopScorer, Standing, Coach, Player, Area

class TeamSerializer(serializers.ModelSerializer):
    area_name = serializers.CharField(source='area.name', read_only=True, default='Unknown')
    area_code = serializers.CharField(source='area.code', read_only=True, allow_null=True)
    area_flag = serializers.URLField(source='area.flag', read_only=True, allow_null=True)

    class Meta:
        model = Team
        fields = [
            'id', 'name', 'short_name', 'tla', 'crest',
            'address', 'website', 'founded', 'club_colors',
            'venue', 'area', 'area_name', 'area_code', 'area_flag'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        # Use actual data if available, otherwise use fallbacks
        if instance.name:
            data['name'] = instance.name
        elif instance.short_name:
            data['name'] = instance.short_name
        else:
            data['name'] = f"Team {instance.id}"

        if instance.short_name:
            data['short_name'] = instance.short_name
        elif instance.name:
            data['short_name'] = instance.name.split()[0]
        else:
            data['short_name'] = f"T{instance.id}"

        if instance.tla:
            data['tla'] = instance.tla
        elif instance.short_name:
            data['tla'] = instance.short_name[:3].upper()
        elif instance.name:
            data['tla'] = instance.name[:3].upper()
        else:
            data['tla'] = f"T{instance.id}"[:3].upper()
        
        # Set defaults for optional fields only if they're None
        defaults = {
            'venue': 'No Venue',
            'founded': None,
            'crest': f'https://crests.football-data.org/{instance.id}.png',
            'club_colors': 'Not Available',
            'website': '#',
            'address': 'No Address',
            'area_name': 'Unknown',
        }
        
        for field, default in defaults.items():
            if data.get(field) is None:
                data[field] = default
            
        return data

class CompetitionSerializer(serializers.ModelSerializer):
    area_name = serializers.CharField(source='area.name', read_only=True)
    season = serializers.SerializerMethodField()

    def get_season(self, obj):
        # Get the most recent season for this competition
        latest_match = Match.objects.filter(
            competition=obj,
            season__isnull=False
        ).order_by('-match_date').first()
        return latest_match.season if latest_match else None

    class Meta:
        model = Competition
        fields = ['id', 'name', 'code', 'area', 'area_name', 'type', 'emblem', 'season']

class MatchSerializer(serializers.ModelSerializer):
    competition_name = serializers.CharField(source='competition.name', read_only=True, default='')
    home_team_name = serializers.CharField(source='home_team.name', read_only=True, default='')
    away_team_name = serializers.CharField(source='away_team.name', read_only=True, default='')
    home_team_crest = serializers.URLField(source='home_team.crest', read_only=True, default='')
    away_team_crest = serializers.URLField(source='away_team.crest', read_only=True, default='')
    area_name = serializers.CharField(source='area.name', read_only=True, default='')

    class Meta:
        model = Match
        fields = [
            'id', 'competition', 'competition_name', 
            'match_date', 'status', 'stage',
            'home_team', 'home_team_name', 'home_team_crest',
            'away_team', 'away_team_name', 'away_team_crest',
            'home_team_score', 'away_team_score',
            'season', 'area', 'area_name'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Ensure required fields have default values
        data['competition_name'] = data.get('competition_name') or 'Unknown Competition'
        data['home_team_name'] = data.get('home_team_name') or 'Unknown Team'
        data['away_team_name'] = data.get('away_team_name') or 'Unknown Team'
        data['status'] = instance.status or 'SCHEDULED'
        data['stage'] = instance.stage or 'Regular Season'
        return data

class TopScorerSerializer(serializers.ModelSerializer):
    player_name = serializers.SerializerMethodField()
    team_name = serializers.SerializerMethodField()
    team_crest = serializers.SerializerMethodField()
    player_nationality = serializers.SerializerMethodField()
    
    def get_player_name(self, obj):
        if not obj.player:
            return None
        return obj.player.name
        
    def get_team_name(self, obj):
        if not obj.player or not obj.player.team:
            return None
        return obj.player.team.name
        
    def get_team_crest(self, obj):
        if not obj.player or not obj.player.team:
            return None
        return obj.player.team.crest
        
    def get_player_nationality(self, obj):
        if not obj.player:
            return None
        return obj.player.nationality
    
    class Meta:
        model = TopScorer
        fields = [
            'id', 'player', 'player_name', 'player_nationality',
            'team', 'team_name', 'team_crest',
            'goals', 'assists', 'penalties'
        ]

class StandingSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source='team.name', read_only=True)
    
    class Meta:
        model = Standing
        fields = ['id', 'team', 'team_name', 'position', 'points', 'goals_diff', 'goals_for', 'goals_against', 'played_games']

class CoachSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source='team.name', read_only=True)
    
    class Meta:
        model = Coach
        fields = ['id', 'name', 'date_of_birth', 'team', 'team_name']

class PlayerSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source='team.name', read_only=True, default='')
    age = serializers.SerializerMethodField()

    def get_age(self, obj):
        if not obj.date_of_birth:
            return None
        from datetime import date
        today = date.today()
        return today.year - obj.date_of_birth.year - ((today.month, today.day) < (obj.date_of_birth.month, obj.date_of_birth.day))

    class Meta:
        model = Player
        fields = [
            'id', 'name', 'position', 'date_of_birth', 'nationality',
            'team', 'team_name', 'age'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Ensure required fields have default values
        data['name'] = instance.name or 'Unknown Player'
        data['position'] = instance.position or 'Unknown Position'
        data['nationality'] = instance.nationality or 'Unknown Nationality'
        data['team_name'] = data.get('team_name') or 'Unknown Team'
        return data

class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ['id', 'name', 'code', 'flag']

class TeamAnalyticsSerializer(serializers.ModelSerializer):
    match_statistics = serializers.SerializerMethodField()
    form_analysis = serializers.SerializerMethodField()
    top_scorers = serializers.SerializerMethodField()
    
    class Meta:
        model = Team
        fields = ['id', 'name', 'match_statistics', 'form_analysis', 'top_scorers']
    
    def get_match_statistics(self, obj):
        home_matches = Match.objects.filter(home_team=obj)
        away_matches = Match.objects.filter(away_team=obj)
        
        home_stats = home_matches.aggregate(
            matches_played=Count('id'),
            goals_scored=Sum('home_team_score'),
            goals_conceded=Sum('away_team_score'),
            wins=Count('id', filter=Q(home_team_score__gt=F('away_team_score'))),
            draws=Count('id', filter=Q(home_team_score=F('away_team_score'))),
            losses=Count('id', filter=Q(home_team_score__lt=F('away_team_score')))
        )
        
        away_stats = away_matches.aggregate(
            matches_played=Count('id'),
            goals_scored=Sum('away_team_score'),
            goals_conceded=Sum('home_team_score'),
            wins=Count('id', filter=Q(away_team_score__gt=F('home_team_score'))),
            draws=Count('id', filter=Q(away_team_score=F('home_team_score'))),
            losses=Count('id', filter=Q(away_team_score__lt=F('home_team_score')))
        )
        
        return {
            'total_matches': (home_stats['matches_played'] or 0) + (away_stats['matches_played'] or 0),
            'total_goals_scored': (home_stats['goals_scored'] or 0) + (away_stats['goals_scored'] or 0),
            'total_goals_conceded': (home_stats['goals_conceded'] or 0) + (away_stats['goals_conceded'] or 0),
            'total_wins': (home_stats['wins'] or 0) + (away_stats['wins'] or 0),
            'total_draws': (home_stats['draws'] or 0) + (away_stats['draws'] or 0),
            'total_losses': (home_stats['losses'] or 0) + (away_stats['losses'] or 0),
            'home_performance': home_stats,
            'away_performance': away_stats
        }
    
    def get_form_analysis(self, obj):
        recent_matches = Match.objects.filter(
            Q(home_team=obj) | Q(away_team=obj)
        ).order_by('-match_date')[:5]
        
        form = []
        for match in recent_matches:
            if match.home_team == obj:
                if match.home_team_score > match.away_team_score:
                    form.append({'result': 'W', 'score': f"{match.home_team_score}-{match.away_team_score}"})
                elif match.home_team_score < match.away_team_score:
                    form.append({'result': 'L', 'score': f"{match.home_team_score}-{match.away_team_score}"})
                else:
                    form.append({'result': 'D', 'score': f"{match.home_team_score}-{match.away_team_score}"})
            else:
                if match.away_team_score > match.home_team_score:
                    form.append({'result': 'W', 'score': f"{match.away_team_score}-{match.home_team_score}"})
                elif match.away_team_score < match.home_team_score:
                    form.append({'result': 'L', 'score': f"{match.away_team_score}-{match.home_team_score}"})
                else:
                    form.append({'result': 'D', 'score': f"{match.away_team_score}-{match.home_team_score}"})
        return form
    
    def get_top_scorers(self, obj):
        return TopScorerSerializer(
            TopScorer.objects.filter(team=obj).order_by('-goals')[:5],
            many=True
        ).data

class CompetitionAnalyticsSerializer(serializers.ModelSerializer):
    overview = serializers.SerializerMethodField()
    standings = serializers.SerializerMethodField()
    top_scorers = serializers.SerializerMethodField()
    goals_per_matchday = serializers.SerializerMethodField()
    records = serializers.SerializerMethodField()

    class Meta:
        model = Competition
        fields = ['id', 'name', 'overview', 'standings', 'top_scorers', 'goals_per_matchday', 'records']

    def get_overview(self, obj):
        matches = Match.objects.filter(competition=obj)
        total_goals = matches.aggregate(
            total=Sum('home_team_score', default=0) + Sum('away_team_score', default=0)
        )['total'] or 0
        
        matches_played = matches.count()
        total_teams = Team.objects.filter(
            Q(home_matches__competition=obj) | Q(away_matches__competition=obj)
        ).distinct().count()

        return {
            'total_teams': total_teams,
            'matches_played': matches_played,
            'total_goals': total_goals,
            'goals_per_match': round(total_goals / matches_played if matches_played > 0 else 0, 2),
            'cards_per_match': 0,  # Add if you have cards data
        }

    def get_standings(self, obj):
        teams = Team.objects.filter(
            Q(home_matches__competition=obj) | Q(away_matches__competition=obj)
        ).distinct()
        
        standings = []
        for team in teams:
            home_matches = Match.objects.filter(competition=obj, home_team=team)
            away_matches = Match.objects.filter(competition=obj, away_team=team)
            
            home_stats = home_matches.aggregate(
                wins=Count('id', filter=Q(home_team_score__gt=F('away_team_score'))),
                draws=Count('id', filter=Q(home_team_score=F('away_team_score'))),
                losses=Count('id', filter=Q(home_team_score__lt=F('away_team_score'))),
                goals_for=Sum('home_team_score', default=0),
                goals_against=Sum('away_team_score', default=0)
            )
            
            away_stats = away_matches.aggregate(
                wins=Count('id', filter=Q(away_team_score__gt=F('home_team_score'))),
                draws=Count('id', filter=Q(away_team_score=F('home_team_score'))),
                losses=Count('id', filter=Q(away_team_score__lt=F('home_team_score'))),
                goals_for=Sum('away_team_score', default=0),
                goals_against=Sum('home_team_score', default=0)
            )
            
            total_wins = (home_stats['wins'] or 0) + (away_stats['wins'] or 0)
            total_draws = (home_stats['draws'] or 0) + (away_stats['draws'] or 0)
            total_losses = (home_stats['losses'] or 0) + (away_stats['losses'] or 0)
            total_matches = total_wins + total_draws + total_losses
            goals_for = (home_stats['goals_for'] or 0) + (away_stats['goals_for'] or 0)
            goals_against = (home_stats['goals_against'] or 0) + (away_stats['goals_against'] or 0)
            
            standings.append({
                'id': team.id,
                'name': team.name,
                'matches_played': total_matches,
                'wins': total_wins,
                'draws': total_draws,
                'losses': total_losses,
                'goals_for': goals_for,
                'goals_against': goals_against,
                'goal_difference': goals_for - goals_against,
                'points': (total_wins * 3) + total_draws
            })
        
        return sorted(standings, key=lambda x: (-x['points'], -x['goal_difference'], -x['goals_for']))

    def get_top_scorers(self, obj):
        return TopScorer.objects.filter(competition=obj) \
            .values('id', 'player_name', 'goals', 'assists') \
            .order_by('-goals')[:10]

    def get_goals_per_matchday(self, obj):
        matches = Match.objects.filter(competition=obj).order_by('match_date')
        goals_data = []
        total_goals = 0
        total_matches = 0
        
        for match in matches:
            if match.home_team_score is not None and match.away_team_score is not None:
                match_goals = match.home_team_score + match.away_team_score
                total_goals += match_goals
                total_matches += 1
                average = round(total_goals / total_matches if total_matches > 0 else 0, 2)
                
                goals_data.append({
                    'matchday': total_matches,
                    'goals': match_goals,
                    'average': average
                })
        
        return goals_data

    def get_records(self, obj):
        matches = Match.objects.filter(competition=obj)
        highest_score = None
        most_goals = 0
        
        for match in matches:
            if match.home_team_score is not None and match.away_team_score is not None:
                total_goals = match.home_team_score + match.away_team_score
                score = f"{match.home_team_score}-{match.away_team_score}"
                
                if total_goals > most_goals:
                    most_goals = total_goals
                    highest_score = score
        
        return {
            'highest_score': highest_score or "0-0",
            'most_goals_in_match': most_goals
        }

class MatchAnalyticsSerializer(serializers.ModelSerializer):
    home_team_name = serializers.CharField(source='home_team.name', read_only=True)
    away_team_name = serializers.CharField(source='away_team.name', read_only=True)
    home_team_crest = serializers.URLField(source='home_team.crest', read_only=True)
    away_team_crest = serializers.URLField(source='away_team.crest', read_only=True)
    competition_name = serializers.CharField(source='competition.name', read_only=True)
    competition_emblem = serializers.CharField(source='competition.emblem', read_only=True)
    head_to_head = serializers.SerializerMethodField()
    team_form = serializers.SerializerMethodField()
    
    class Meta:
        model = Match
        fields = [
            'id', 'match_date', 
            'home_team', 'home_team_name', 'home_team_crest', 'home_team_score',
            'away_team', 'away_team_name', 'away_team_crest', 'away_team_score',
            'competition', 'competition_name', 'competition_emblem', 'status',
            'head_to_head', 'team_form'
        ]
    
    def get_head_to_head(self, obj):
        previous_matches = Match.objects.filter(
            Q(home_team=obj.home_team, away_team=obj.away_team) |
            Q(home_team=obj.away_team, away_team=obj.home_team)
        ).exclude(id=obj.id).order_by('-match_date')[:5]
        
        return [{
            'date': match.match_date,
            'home_team': match.home_team.name,
            'away_team': match.away_team.name,
            'score': f"{match.home_team_score}-{match.away_team_score}"
        } for match in previous_matches]
    
    def get_team_form(self, obj):
        home_form = self._get_team_form(obj.home_team)
        away_form = self._get_team_form(obj.away_team)
        return {
            'home_team': home_form,
            'away_team': away_form
        }
    
    def _get_team_form(self, team):
        recent_matches = Match.objects.filter(
            Q(home_team=team) | Q(away_team=team)
        ).order_by('-match_date')[:5]
        
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
        return ''.join(form)

class PlayerAnalyticsSerializer(serializers.ModelSerializer):
    season_statistics = serializers.SerializerMethodField()
    recent_performances = serializers.SerializerMethodField()
    
    class Meta:
        model = Player
        fields = ['id', 'name', 'season_statistics', 'recent_performances']
    
    def get_season_statistics(self, obj):
        scorer_stats = TopScorer.objects.filter(player=obj).aggregate(
            total_goals=Sum('goals'),
            total_assists=Sum('assists'),
            matches_played=Sum('played_matches')
        )
        
        if scorer_stats['matches_played'] and scorer_stats['total_goals']:
            scorer_stats['goals_per_match'] = round(
                scorer_stats['total_goals'] / scorer_stats['matches_played'], 2
            )
        else:
            scorer_stats['goals_per_match'] = 0
            
        return scorer_stats
    
    def get_recent_performances(self, obj):
        recent_scores = TopScorer.objects.filter(player=obj).order_by('-season')[:5]
        return TopScorerSerializer(recent_scores, many=True).data
