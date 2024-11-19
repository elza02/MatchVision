from kafka import KafkaConsumer
import json

# Initialize the consumer with the topic and deserializer
consumer = KafkaConsumer(
    'football_standings',  # Topic name
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda x: json.loads(x.decode('utf-8')) if x else None  # Check for empty messages
)

# Process incoming messages
for message in consumer:
    try:
        standings_data = message.value  # Already deserialized by value_deserializer
        if standings_data:
            #print(f"Received data: {standings_data}")
            # Accessing the standings table, handling potential KeyError
            standings = standings_data.get('standings', [])
            if standings and 'table' in standings[0]:
                for team in standings[0]['table']:
                    print(f"{team['position']}. {team['team']['name']} - {team['points']} points")
            else:
                print("Standings data not found in message.")
        else:
            print("Empty message received.")
    except KeyError as e:
        print(f"Key error: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding message: {e}")


# team variable structure example => {'position': 19, 'team': {'id': 76, 'name': 'Wolverhampton Wanderers FC', 
#           'shortName': 'Wolverhampton', 'tla': 'WOL', 'crest': 'https://crests.football-data.org/76.png'}, 
#           'playedGames': 11, 'form': None, 'won': 1, 'draw': 3, 'lost': 7, 'points': 6, 'goalsFor': 16, 
#           'goalsAgainst': 27, 'goalDifference': -11}