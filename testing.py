def get_match_data():
    # Fetch match data from Football-data API
    url = "https://api.football-data.org/v2/competitions/PL/matches"
    headers = {'X-Auth-Token': 'YOUR_API_KEY'}
    response = requests.get(url, headers=headers)
    data = response.json()
    return data['matches']