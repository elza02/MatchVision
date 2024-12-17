from flask import Flask, render_template, request
import requests
import json
from datetime import datetime
import http 
import matplotlib.pyplot as plt
import pandas as pd


app = Flask(__name__)

# API details
# Load API key
with open('key.json') as config_file:
    config = json.load(config_file)
API_KEY = config['api_key']
RAPID_API_KEY = config['x-rapidapi-key']
API_BASE_URL = 'https://api.football-data.org/v4'
# Fetch today's match
def get_today_match():
    # Get today's date in the format that the API uses (yyyy-mm-dd)
    today_date = datetime.now().strftime('%Y-%m-%d')
    url = 'https://api.football-data.org/v4/matches'
    # Make the API request
    headers = {'X-Auth-Token': API_KEY}
    response = requests.get(url, headers=headers)
    
    data = response.json()

    # Filter the matches for today's date
    today_matches = [match for match in data['matches'] if match['utcDate'][:10] == today_date]

    # If we have any matches, return the first one (if there are multiple, you can modify this logic)
    if today_matches:
        return today_matches  # We only show the first match of the day for now
    else:
        return None


def get_league_code_by_id(league_id):
    url = f"https://api.football-data.org/v4/competitions/{league_id}"
    headers = {'X-Auth-Token': API_KEY}
    response = requests.get(url, headers=headers)
    
    # Check for successful response
    if response.status_code == 200:
        data = response.json()
        return data.get('code')  # Return the league code
    else:
        return f"Error: {response.status_code} - {response.text}"
    

# Fetch Premier League standings
def get_standings(league_id):
    code = get_league_code_by_id(league_id)
    url = f"https://api.football-data.org/v4/competitions/{code}/standings"
    headers = {'X-Auth-Token': API_KEY}
    response = requests.get(url, headers=headers)

    return response.json()['standings'][0]['table']
# Fetch Top Scorers
def get_top_scorers(id):
    code = get_league_code_by_id(id)
    url = f"https://api.football-data.org/v4/competitions/{code}/scorers"
    headers = {'X-Auth-Token': API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        scorers_data = response.json()['scorers']
        return [
            {
                'player': scorer['player'],
                'goals': scorer['goals'],
                'team': scorer['team'],
                'crest': scorer['team']['crest']
            }
            for scorer in scorers_data[:10]  # Top 10 scorers
        ]
    else:
        return '404'
    


# Fetch all teams in the league
def get_all_teams():
    url = "https://api.football-data.org/v4/competitions/PL/teams"
    headers = {'X-Auth-Token': API_KEY}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        teams_data = response.json()['teams']
        return [
            {
                'id': team['id'],
                'name': team['name'],
                'shortName': team['shortName'],
                'crest': team['crest'],
                'venue': team['venue'],
                'founded': team['founded'],
                'website': team['website']
            }
            for team in teams_data
        ]
    else:
        print("Failed to fetch teams")
        return []

# Fetch team details (formation and stats)
def get_team_details(team_id):
    url = f"https://api.football-data.org/v4/teams/{team_id}"
    headers = {'X-Auth-Token': API_KEY}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        team_data = response.json()
        return {
            'name': team_data['name'],
            'crest': team_data['crest'],
            'venue': team_data['venue'],
            'founded': team_data['founded'],
            'clubColors': team_data['clubColors'],
            'squad': team_data['squad'],  # Player details
            'website': team_data['website'],
        }
    else:
        print(f"Failed to fetch details for team {team_id}")
        return None

def get_player_data(player_id):
    url = f"https://api.football-data.org/v4/persons/{player_id}"
    headers = {'X-Auth-Token': API_KEY}
    response = requests.get(url, headers=headers)
    player = response.json()
    return {
            #'photo': player['crest'],
            'name': player['name'],
            'position': player['position'],
            'nationality': player['nationality'],
            'dateOfBirth': player['dateOfBirth'],  # Player details
            'shirtNumber': player['shirtNumber'],
        }


def test_data():
    url = "https://api.football-data.org/v4/competitions/CL/standings?season=2024"
    headers = {'X-Auth-Token': API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        testD = response.json()
        print(testD)
    else:
        print('the url dont have any data to bring')


def getFeed():
    conn = http.client.HTTPSConnection("twitter241.p.rapidapi.com")

    headers = {
        'x-rapidapi-key': RAPID_API_KEY,
        'x-rapidapi-host': "twitter241.p.rapidapi.com"
    }

    conn.request("GET", "/user-tweets?user=330262748&count=2", headers=headers)

    res = conn.getresponse()
    data = res.read()
    data_str = data.decode("utf-8")
    json_data = json.loads(data_str)
    info = json_data['result']['timeline']['instructions'][2]['entries']#[0]['content']['itemContent']['tweet_results']['result']['legacy']['retweeted_status_result']['result']['legacy']['full_text']
    print(len(json_data))
    return info

def get_available_leagues():
    url = "https://api.football-data.org/v4/competitions"
    headers = {'X-Auth-Token': API_KEY}
    response = requests.get(url, headers=headers)
    leagues = response.json().get('competitions', [])
    # Filter only free leagues (you may need to check which leagues are free)
    return leagues


def generate_plots(data, league):
    plots = {}

    # 1. Top Teams by Elo Rating
    top_teams = data.groupby('team')['elo'].max().sort_values(ascending=False).head(10)
    plt.figure(figsize=(10, 6))
    top_teams.plot(kind='bar', color='skyblue')
    plt.title('Top 10 Teams by Elo Rating')
    plt.ylabel('Elo Rating')
    plt.xlabel('Team')
    plot_path = f'static/stats/{league}_plots/top_teams.png'
    plt.savefig(plot_path)
    plots['top_teams'] = plot_path
    plt.close()

    # 2. Average Elo Rating by Week
    data['week'] = pd.to_datetime(data['week'])  # Convert weeks to datetime
    weekly_avg_elo = data.groupby('week')['elo'].mean()
    plt.figure(figsize=(10, 6))
    weekly_avg_elo.plot(color='green')
    plt.title('Average Elo Rating Over Time')
    plt.ylabel('Average Elo')
    plt.xlabel('Week')
    plot_path = f'static/stats/{league}_plots/weekly_avg_elo.png'
    plt.savefig(plot_path)
    plots['weekly_avg_elo'] = plot_path
    plt.close()

    # 3. Rank Distribution
    rank_counts = data['rank'].value_counts().head(10)
    plt.figure(figsize=(10, 6))
    rank_counts.plot(kind='bar', color='coral')
    plt.title('Rank Distribution (Top 10 Ranks)')
    plt.ylabel('Frequency')
    plt.xlabel('Rank')
    plot_path = f'static/stats/{league}_plots/rank_distribution.png'
    plt.savefig(plot_path)
    plots['rank_distribution'] = plot_path
    plt.close()

    return plots

@app.route('/')
def index():
    # Get today's match, standings, top scorers, and top assists
    info = getFeed()
    # match_of_the_day = get_today_match()
    # standings_data = get_standings()
    # top_scorers = get_top_scorers()
    # top_assists = get_top_assists()

    # Pass data to the template
    return render_template('index.html', info = info)#, top_assists=top_assists)

@app.route('/league/<int:league_id>')
def leagues_team(league_id):
    # Get today's match, standings, top scorers, and top assists
    # print(league_id)
    standings_data = get_standings(league_id)
    
    if get_top_scorers(league_id) != '404':
        top_scorers = get_top_scorers(league_id)
    else:
        top_scorers = None
    # top_assists = get_top_assists()

    # Pass data to the template
    return render_template('PL.html', standings_data=standings_data,
                           top_scorers=top_scorers)#, top_assists=top_assists)


# Route to display all teams
@app.route('/teams')
def teams():
    teams_data = get_all_teams()
    # print(teams_data)
    return render_template('teams.html', teams=teams_data)

# Route to display details of a single team
@app.route('/team/<int:team_id>')
def team_details(team_id):
    team_data = get_team_details(team_id)
    print(team_data)
    return render_template('team_details.html', team=team_data)


@app.route('/player/<int:player_id>')
def player_details(player_id):
    # Fetch player details using player_id
    player_data = get_player_data(player_id)
    return render_template('player_details.html', player=player_data)





@app.route('/test')
def test():
    teams_data = test_data()
    # print(teams_data)
    #return render_template('teams.html', teams=teams_data)



@app.route('/leagues')
def leagues():
    # Assuming you have a function `get_available_leagues()` which fetches leagues from the API
    leagues = get_available_leagues()
    print(leagues)
    return render_template('leagues.html', leagues=leagues)

@app.route('/today-matches')
def today_matches():
    # Assuming you have a function `get_today_match()` which fetches today's matches
    matches = get_today_match()
    # a cree un objet vide avec les mm attribut.
    
    return render_template('today_matches.html', matches=matches)

@app.route('/statistics')
def stats1():
    # Generate plots and get their paths
    data = pd.read_csv('static/stats/ENG_Premier_League_elo.csv')

    plots = generate_plots(data, 'PL')

    #print(plots)
    
    # Compute additional statistics
    top_team = data.loc[data['elo'].idxmax(), 'team']
    top_elo = data['elo'].max()
    avg_elo = data['elo'].mean()

    stats = {
        "top_team": top_team,
        "top_elo": round(top_elo, 2),
        "avg_elo": round(avg_elo, 2)
    }
    
    return render_template('statistics.html', plots=plots, stats=stats, league='PL')

@app.route('/statistics/<string:league>')
def stats2(league):
    # Generate plots and get their paths
    if league == 'PL':
        data = pd.read_csv('static/stats/ENG_Premier_League_elo.csv')
    elif league ==  'FR':
        data = pd.read_csv('static/stats/FRA_Ligue_1_elo.csv')
    elif league ==  'IT':
        data = pd.read_csv('static/stats/ITA_Serie_A_elo.csv')
    elif league ==  'GR':
        data = pd.read_csv('static/stats/GER_Bundesliga_elo.csv')

    plots = generate_plots(data, league)

    #print(plots)
    
    # Compute additional statistics
    top_team = data.loc[data['elo'].idxmax(), 'team']
    top_elo = data['elo'].max()
    avg_elo = data['elo'].mean()

    stats = {
        "top_team": top_team,
        "top_elo": round(top_elo, 2),
        "avg_elo": round(avg_elo, 2)
    }
    
    return render_template('statistics.html', plots=plots, stats=stats, league=league)

def fetch_team_statistics(team_id):
    """Fetch statistics for a team."""
    headers = {'X-Auth-Token': API_KEY}
    url = f'{API_BASE_URL}/teams/{team_id}/matches'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()['matches']
    return None

def calculate_recent_form(matches, team_id):
    """Calculate recent form (last 5 matches) for a team."""
    recent_matches = [match for match in matches if match['status'] == 'FINISHED'][:10]
    wins, draws, losses, goals_scored, goals_conceded = 0, 0, 0, 0, 0

    for match in recent_matches:
        is_home_team = match['homeTeam']['id'] == team_id
        is_away_team = match['awayTeam']['id'] == team_id

        if is_home_team or is_away_team:
            # Determine goals scored and conceded
            if is_home_team:
                goals_scored += match['score']['fullTime']['home']
                goals_conceded += match['score']['fullTime']['away']
                if match['score']['winner'] == 'HOME_TEAM':
                    wins += 1
                elif match['score']['winner'] == 'AWAY_TEAM':
                    losses += 1
                else:
                    draws += 1
            elif is_away_team:
                goals_scored += match['score']['fullTime']['away']
                goals_conceded += match['score']['fullTime']['home']
                if match['score']['winner'] == 'AWAY_TEAM':
                    wins += 1
                elif match['score']['winner'] == 'HOME_TEAM':
                    losses += 1
                else:
                    draws += 1

    return {
        'wins': wins,
        'draws': draws,
        'losses': losses,
        'goals_scored': goals_scored,
        'goals_conceded': goals_conceded,
        'matches': len(recent_matches),
    }


@app.route('/match-prediction')
def match_statistics():
    """Show the statistics and prediction for a match between two teams."""
    team1 = request.args.get('team1')
    team2 = request.args.get('team2')

    # Fetch team statistics
    home_team_matches = fetch_team_statistics(int(team1))
    away_team_matches = fetch_team_statistics(int(team2))

    # Fetch team names
    home_team_name = home_team_matches[0]['homeTeam']['name']
    away_team_name = away_team_matches[0]['awayTeam']['name']

    # Fetch team logo
    home_team_logo = home_team_matches[0]['homeTeam']['crest']
    away_team_logo = away_team_matches[0]['awayTeam']['crest']

    # Calculate recent form
    home_form = calculate_recent_form(home_team_matches, int(team1))
    away_form = calculate_recent_form(away_team_matches, int(team2))

    # Calculate win probabilities (basic model based on recent wins and goals scored)
    home_score = (
        home_form['wins'] * 3 + home_form['goals_scored'] - home_form['goals_conceded']
    )
    away_score = (
        away_form['wins'] * 3 + away_form['goals_scored'] - away_form['goals_conceded']
    )
    total_score = home_score + away_score

    home_win_percentage = (
        (home_score / total_score) * 100 if total_score > 0 else 50
    )
    away_win_percentage = (
        (away_score / total_score) * 100 if total_score > 0 else 50
    )
    prediction = ''
    if home_win_percentage > away_win_percentage:
        prediction = f"{home_team_name} will win"
    elif home_win_percentage < away_win_percentage:
        prediction = f"{away_team_name} will win"
    else:
        prediction = "It's likely a draw"
    # Render the statistics and prediction
    return render_template(
        'match_prediction.html',
        home_team_logo = home_team_logo,
        away_team_logo = away_team_logo,
        home_form=home_form,
        away_form=away_form,
        home_team_name=home_team_name,
        away_team_name=away_team_name,
        prediction = prediction,
        home_win_percentage=round(home_win_percentage, 2),
        away_win_percentage=round(away_win_percentage, 2),
    )


if __name__ == '__main__':
    app.run(debug=True)































# Fetch Top Assists
# def get_top_assists():
#     url = "https://api.football-data.org/v4/competitions/PL/assists"
#     headers = {'X-Auth-Token': API_KEY}
#     response = requests.get(url, headers=headers)

#     if response.status_code == 200:
#         assists_data = response.json()['assists']
#         return [
#             {
#                 'player': assist['player'],
#                 'assists': assist['numberOfAssists'],
#                 'team': assist['team'],
#                 'crest': assist['team']['crest']
#             }
#             for assist in assists_data[:5]  # Top 5 assists
#         ]
#     else:
#         print("Failed to fetch top assists")
#         return []