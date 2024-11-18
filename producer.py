from kafka import KafkaProducer
import requests
import json


producer = KafkaProducer(bootstrap_servers='localhost:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))

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

match_data = get_match_data()

for match in match_data:
    producer.send('premier_league_results', match)


def get_standing():
    # Fetch match data from Football-data API
    url = "https://api.football-data.org/v4/competitions/PL/standings"
    headers = {'X-Auth-Token': api_key}
    response = requests.get(url, headers=headers)
    return response.json()




producer.flush()
