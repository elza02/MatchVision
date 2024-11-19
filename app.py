from flask import Flask, render_template
import requests
import json
from datetime import datetime

app = Flask(__name__)

# API details
# Load API key
with open('key.json') as config_file:
    config = json.load(config_file)
API_KEY = config['api_key']

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

# Fetch Premier League standings
def get_standings():
    url = "https://api.football-data.org/v4/competitions/PL/standings"
    headers = {'X-Auth-Token': API_KEY}
    response = requests.get(url, headers=headers)

    return response.json()['standings'][0]['table']
# Fetch Top Scorers
def get_top_scorers():
    url = "https://api.football-data.org/v4/competitions/PL/scorers"
    headers = {'X-Auth-Token': API_KEY}
    response = requests.get(url, headers=headers)

    scorers_data = response.json()['scorers']
    return [
        {
            'player': scorer['player'],
            'goals': scorer['goals'],
            'team': scorer['team'],
            'crest': scorer['team']['crest']
        }
        for scorer in scorers_data[:5]  # Top 5 scorers
    ]




@app.route('/')
def index():
    # Get today's match, standings, top scorers, and top assists
    match_of_the_day = get_today_match()
    standings_data = get_standings()
    top_scorers = get_top_scorers()
    # top_assists = get_top_assists()

    # Pass data to the template
    return render_template('index.html', match_of_the_day=match_of_the_day, standings_data=standings_data,
                           top_scorers=top_scorers)#    , top_assists=top_assists)

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