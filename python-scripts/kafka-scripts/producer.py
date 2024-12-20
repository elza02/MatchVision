import requests
from kafka import KafkaProducer
import json
import os
import time

# Configuration
API_BASE_URL = "http://api.football-data.org/v4/"
HEADERS = {"X-Auth-Token": os.getenv("FOOTBALL_API_KEY", "8bdeca631d7b495d81f502451792f341")}
KAFKA_BROKER = "kafka:29092"
TOPICS = {
    "teams": "teams-topic",
    "competitions": "competitions-topic",
    "matches": "matches-topic",
    "top_scorers": "top-scorers-topic",
    "standings": "standings-topic",
    "players": "players-topic",
}

# Initialize Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)


def fetch_competitions():
    try:
        response = requests.get(f"{API_BASE_URL}competitions/", headers=HEADERS)
        response.raise_for_status()
        competitions = response.json().get("competitions", [])

        producer.send(TOPICS["competitions"], value=competitions)
        producer.flush()
        print(f"Produced {len(competitions)} competitions to Kafka.")
        competition_codes = [c["code"] for c in competitions]
        competition_names = [c["name"] for c in competitions]
        return competition_codes, competition_names
    except Exception as e:
        print(f"Error fetching competitions: {e}")
        return []


def fetch_teams_by_competition(competition_code, season):
    try:
        response = requests.get(f"{API_BASE_URL}competitions/{competition_code}/teams?season={season}", headers=HEADERS)
        response.raise_for_status()
        teams = response.json().get("teams", [])
        competition = response.json().get("competition", {}) if response else "Unknown"

        data = {"season": season, "competition": competition, "teams": teams}
        
        producer.send(TOPICS["teams"], value=data)
        producer.flush()
        print(f"Produced {len(teams)} teams.")
    except Exception as e:
        print(f"Error fetching teams for competition {response.json().get('competition', {}).get('name', '')}: {e}")
        return {}


def fetch_matches_by_competition(competition_code, season):
    try:
        response = requests.get(f"{API_BASE_URL}competitions/{competition_code}/matches?season={season}", headers=HEADERS)
        response.raise_for_status()
        matches = response.json().get("matches", [])
        competition = response.json().get("competition", {}) if response else "Unknown"
        data = {"season": season, "competition": competition, "matches": matches}        

        producer.send(TOPICS["matches"], value=data)
        producer.flush()
        print(f"Produced {len(matches)} matches for competition {response.json().get('competition', {}).get('name', '')}, season {season}.")
    except Exception as e:
        print(f"Error fetching matches for competition {response.json().get('competition', {}).get('name', '')}, season {season}: {e}")


def fetch_top_scorers(competition_code, season):
    try:
        response = requests.get(f"{API_BASE_URL}competitions/{competition_code}/scorers?season={season}", headers=HEADERS)
        response.raise_for_status()
        scorers = response.json().get("scorers", [])
        competition = response.json().get("competition", {}) if response else "Unknown"
        
        data = {"season": season, "competition": competition, "scorers": scorers}
        producer.send(TOPICS["top_scorers"], value=data)
        producer.flush()
        print(f"Produced {len(scorers)} top scorers for competition {response.json().get('competition', {}).get('name', '')}, season {season}.")
    except Exception as e:
        print(f"Error fetching top scorers for competition {response.json().get('competition', {}).get('name', '')}, season {season}: {e}")

def fetch_standings(competition_code, season):
    try:
        response = requests.get(f"{API_BASE_URL}competitions/{competition_code}/standings?season={season}", headers=HEADERS)
        response.raise_for_status()
        standings = response.json()
        competition = response.json().get("competition", {}) if response else "Unknown"
        
        data = {"season": season, "competition": competition, "standings": standings}
        
        producer.send(TOPICS["standings"], value=data)
        producer.flush()
        print(f"Produced {len(standings)} standings for competition {response.json().get('competition', {}).get('name', '')}, season {season}.")
    except Exception as e:
        print(f"Error fetching standings for competition {response.json().get('competition', {}).get('name', '')}, season {season}: {e}")
        

def fetch_players():
    pass                
    

# Main process
def main():
    """Fetch data from the football-data API and produce to Kafka topics."""
    competition_codes, competition_names = fetch_competitions() ## competitions
    seasons = [2022, 2023, 2024]
    
    # Fetch data for each competition and season
    for competition_code, competition_name in zip(competition_codes, competition_names):
        for season in seasons:

            print(f"Fetching teams for competition {competition_name}...")
            try:
                fetch_teams_by_competition(competition_code, season) ## teams     
            except Exception as e:
                print(f"Skipping teams for competition {competition_name} due to error: {e}")
            time.sleep(6)
            
            print(f"Fetching matches for competition {competition_name}, season {season}...")
            try:
                fetch_matches_by_competition(competition_code, season) ## matches
            except Exception as e:
                print(f"Skipping matches for competition {competition_name}, season {season} due to error: {e}")
            time.sleep(6)

            print(f"Fetching top scorers for competition {competition_name}, season {season}...")
            try:
                fetch_top_scorers(competition_code, season) ## top scorers
            except Exception as e:
                print(f"Skipping top scorers for competition {competition_code}, season {season} due to error: {e}")
            time.sleep(6)
            
            print(f"Fetching standings for competition {competition_name}, season {season}...")
            try:
                fetch_standings(competition_code, season) ## standings
            except Exception as e:
                print(f"Skipping standings for competition {competition_code}, season {season} due to error: {e}")
            time.sleep(6)
            


if __name__ == "__main__":
    main()
