from kafka import KafkaProducer
import requests
import json


producer = KafkaProducer(bootstrap_servers='localhost:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))

with open('key.json') as config_file:
    config = json.load(config_file)
api_key = config['api_key']


def get_standing():
    # Fetch match data from Football-data API
    url = "https://api.football-data.org/v4/competitions/PL/standings"
    headers = {'X-Auth-Token': api_key}
    response = requests.get(url, headers=headers)
    message = response.json()  # You can still use a string here
    producer.send('football_standings', value=message)
    producer.flush()
    producer.close()
    print('sent')




get_standing()
