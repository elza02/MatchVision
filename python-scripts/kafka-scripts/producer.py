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
    "top_scorers": "top-scorers-topic"
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

        for competition in competitions:
            data = {
                "id": competition["id"],
                "name": competition["name"],
                "code": competition["code"],
                "type": competition["type"],
                "emblem": competition["emblem"],
                "area": competition["area"]["name"]
            }
            producer.send(TOPICS["competitions"], value=data)
            print(f"Produced competition: {data}")

        producer.flush()
        print(f"Produced {len(competitions)} competitions to Kafka.")
        return [c["code"] for c in competitions]
    except Exception as e:
        print(f"Error fetching competitions: {e}")
        return []

def fetch_teams(competition_code):
    try:
        response = requests.get(f"{API_BASE_URL}competitions/{competition_code}/teams", headers=HEADERS)
        response.raise_for_status()
        teams = response.json().get("teams", [])

        for team in teams:
            data = {
                "id": team["id"],
                "name": team["name"],
                "venue": team.get("venue", "Unknown Venue")
            }
            producer.send(TOPICS["teams"], value=data)
            print(f"Produced team: {data}")

        producer.flush()
        print(f"Produced {len(teams)} teams for competition {competition_code}.")
        return {t["id"]: t for t in teams}
    except Exception as e:
        print(f"Error fetching teams for competition {competition_code}: {e}")
        return {}

def fetch_matches(competition_code, season, team_map):
    try:
        response = requests.get(f"{API_BASE_URL}competitions/{competition_code}/matches?season={season}", headers=HEADERS)
        response.raise_for_status()
        matches = response.json().get("matches", [])
        competition_id = response.json().get("competition").get("id")

        for match in matches:
            data = {
                "id": match["id"],
                "competition_id": competition_id,
                "season": season,
                "match_date": match["utcDate"],
                "status": match["status"],
                "home_team_id": match["homeTeam"]["id"],
                "away_team_id": match["awayTeam"]["id"],
                "home_team_score": match["score"]["fullTime"].get("home"),
                "away_team_score": match["score"]["fullTime"].get("away"),
                "referee": match.get("referees")[0].get("name") if match.get("referees") else None,
            }
            producer.send(TOPICS["matches"], value=data)
            print(f"Produced match: {data}")

        producer.flush()
        print(f"Produced {len(matches)} matches for competition {competition_id}, season {season}.")
    except Exception as e:
        print(f"Error fetching matches for competition {competition_id}, season {season}: {e}")


def fetch_top_scorers(competition_code, season):
    try:
        response = requests.get(f"{API_BASE_URL}competitions/{competition_code}/scorers?season={season}", headers=HEADERS)
        response.raise_for_status()
        scorers = response.json().get("scorers", [])
        competition_id = response.json().get("competition").get("id")

        for scorer in scorers:
            if scorer["player"].get("id") and scorer["team"].get("id"):
                data = {
                    "player_id": scorer["player"].get("id"),
                    "player_name": scorer["player"].get("name", "Unknown"),
                    "team_id": scorer["team"].get("id"),
                    "competition_id": competition_id,
                    "season": season,
                    "goals": scorer.get("goals", 0),
                    "assists": scorer.get("assists", 0),
                    "playedMatches": scorer.get("playedMatches"),
                    "penalties": scorer.get("penalties", 0),
                }
                producer.send(TOPICS["top_scorers"], value=data)
                print(f"Produced top scorer: {data}")

        producer.flush()
        print(f"Produced {len(scorers)} top scorers for competition {competition_id}, season {season}.")
    except Exception as e:
        print(f"Error fetching top scorers for competition {competition_id}, season {season}: {e}")

def fetch_standigs():
    pass

# Main process
def main():
    competition_codes = fetch_competitions()
    seasons = [2022, 2023, 2024]

    for competition_code in competition_codes:
        print(f"Fetching teams for competition {competition_code}...")
        team_map = fetch_teams(competition_code)
        time.sleep(6)

        for season in seasons:
            print(f"Fetching matches for competition {competition_code}, season {season}...")
            try:
                fetch_matches(competition_code, season, team_map)
            except Exception as e:
                print(f"Skipping matches for competition {competition_code}, season {season} due to error: {e}")
            time.sleep(6)

            print(f"Fetching top scorers for competition {competition_code}, season {season}...")
            try:
                fetch_top_scorers(competition_code, season)
            except Exception as e:
                print(f"Skipping top scorers for competition {competition_code}, season {season} due to error: {e}")
            time.sleep(6)


if __name__ == "__main__":
    main()
