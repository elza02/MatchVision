import os
import django
import random
from datetime import datetime, timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')
django.setup()

from django_app.models import Team, Competition, Match, Player, PlayerStats, MatchPrediction

def clear_data():
    """Clear all data from tables in correct order"""
    print("Clearing existing data...")
    PlayerStats.objects.all().delete()
    MatchPrediction.objects.all().delete()
    Match.objects.all().delete()
    Player.objects.all().delete()
    Team.objects.all().delete()
    Competition.objects.all().delete()

def create_sample_data():
    """Create sample data for the application"""
    print("Creating sample data...")
    
    # Create Competitions
    competitions = []
    competition_data = [
        {'id': 1, 'name': 'Premier League', 'area': 'England'},
        {'id': 2, 'name': 'La Liga', 'area': 'Spain'},
        {'id': 3, 'name': 'Serie A', 'area': 'Italy'}
    ]
    
    print("Creating competitions...")
    for comp_data in competition_data:
        competition = Competition.objects.create(**comp_data)
        competitions.append(competition)
        print(f"Created competition: {competition.name}")

    # Create Teams
    teams_data = [
        {'id': 1, 'name': 'Manchester United', 'venue': 'Old Trafford'},
        {'id': 2, 'name': 'Liverpool', 'venue': 'Anfield'},
        {'id': 3, 'name': 'Barcelona', 'venue': 'Camp Nou'},
        {'id': 4, 'name': 'Real Madrid', 'venue': 'Santiago Bernabeu'},
        {'id': 5, 'name': 'Juventus', 'venue': 'Allianz Stadium'},
        {'id': 6, 'name': 'Inter Milan', 'venue': 'San Siro'}
    ]
    
    teams = []
    print("Creating teams...")
    for team_data in teams_data:
        team = Team.objects.create(**team_data)
        teams.append(team)
        print(f"Created team: {team.name}")

    # Create Players
    positions = ['Forward', 'Midfielder', 'Defender', 'Goalkeeper']
    print("Creating players...")
    for team in teams:
        for i in range(11):  # Create 11 players per team
            player = Player.objects.create(
                id=len(Player.objects.all()) + 1,
                name=f"Player {i+1} - {team.name}",
                position=random.choice(positions),
                nationality='Unknown',
                team=team,
                shirt_number=i+1,
                age=random.randint(18, 35),
                market_value=random.randint(1000000, 100000000)
            )
            print(f"Created player: {player.name}")

    # Create Matches
    statuses = ['SCHEDULED', 'LIVE', 'FINISHED']
    print("Creating matches...")
    for i in range(1, 11):  # Create 10 matches
        home_team = random.choice(teams)
        away_team = random.choice([t for t in teams if t != home_team])
        competition = random.choice(competitions)
        status = random.choice(statuses)
        
        match_date = datetime.now() + timedelta(days=random.randint(-5, 15))
        
        home_score = random.randint(0, 5) if status == 'FINISHED' else None
        away_score = random.randint(0, 5) if status == 'FINISHED' else None
        
        match = Match.objects.create(
            id=i,
            competition=competition,
            season='2023/24',
            home_team=home_team,
            away_team=away_team,
            match_date=match_date,
            status=status,
            home_team_score=home_score,
            away_team_score=away_score,
            referee=f'Referee {i}'
        )
        print(f"Created match: {match}")
        
        # Create match prediction for non-finished matches
        if status != 'FINISHED':
            home_prob = random.uniform(0.2, 0.6)
            draw_prob = random.uniform(0.1, 0.3)
            away_prob = 1 - home_prob - draw_prob
            
            prediction = MatchPrediction.objects.create(
                match=match,
                home_team_win_prob=home_prob,
                draw_prob=draw_prob,
                away_team_win_prob=away_prob,
                predicted_score=f'{random.randint(0, 3)}-{random.randint(0, 3)}'
            )
            print(f"Created prediction for match: {match}")

        # Create player stats for finished matches
        if status == 'FINISHED':
            # Home team players
            for player in Player.objects.filter(team=home_team)[:5]:  # Only create stats for 5 players
                PlayerStats.objects.create(
                    player_id=len(PlayerStats.objects.all()) + 1,
                    name=player.name,
                    position=player.position,
                    goals=random.randint(0, 2),
                    assists=random.randint(0, 2),
                    minutes_played=random.randint(45, 90),
                    team=home_team,
                    match=match
                )
            
            # Away team players
            for player in Player.objects.filter(team=away_team)[:5]:
                PlayerStats.objects.create(
                    player_id=len(PlayerStats.objects.all()) + 1,
                    name=player.name,
                    position=player.position,
                    goals=random.randint(0, 2),
                    assists=random.randint(0, 2),
                    minutes_played=random.randint(45, 90),
                    team=away_team,
                    match=match
                )
            print(f"Created player stats for match: {match}")

if __name__ == '__main__':
    try:
        # Clear existing data
        clear_data()
        
        # Create new sample data
        create_sample_data()
        
        print("\nSample data has been created successfully!")
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
