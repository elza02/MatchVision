import requests
import json


with open('key.json') as config_file:
    config = json.load(config_file)
api_key = config['api_key']


def get_match_data():
    # Fetch match data from Football-data API
    url = "https://api.football-data.org/v2/competitions/PL/matches"
    headers = {'X-Auth-Token': api_key}
    response = requests.get(url, headers=headers)
    data = response.json()
    return data['matches']

