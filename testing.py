import requests
def get_match_data():
    # Fetch match data from Football-data API
    url = "https://api.football-data.org/v2/competitions/PL/matches"
    headers = {'X-Auth-Token': 'ee34a6b82918405a8490a2b9ead8f21b'}
    response = requests.get(url, headers=headers)
    data = response.json()
    return data['matches']

