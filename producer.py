from kafka import KafkaProducer
import requests
import json

producer = KafkaProducer(bootstrap_servers='localhost:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))

def get_match_data():
    # Fetch match data from Football-data API
    url = "https://api.football-data.org/v2/competitions/PL/matches"
    headers = {'X-Auth-Token': 'YOUR_API_KEY'}
    response = requests.get(url, headers=headers)
    data = response.json()
    return data['matches']

match_data = get_match_data()

for match in match_data:
    producer.send('premier_league_results', match)

producer.flush()
