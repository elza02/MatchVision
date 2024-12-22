from pymongo import MongoClient
import mysql.connector
import json
from typing import Dict, Any, Union
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# mongodb database configuration
MONGO_URI = "mongodb://root:houcine@mongodb-football:27017/"
DATABASE_NAME = "football_data"

# mysql database configuration
DB_CONFIG = {
    'host': 'mysql-football',
    'user': 'houcine',
    'password': 'houcine',
    'database': 'football_data'
}

# polling interval
POLLING_INTERVAL = 20


# utils
def add_competition_if_not_exist(competition, area_id, cursor, connection) -> Union[None, int]:
    """Add competition to MySQL if it does not exist using INSERT INTO."""
    """
    COMPETITION MODEL SCHEMA:
    id =
    name = 
    code = 
    type = 
    emblem = 
    area = 
    """
    try:
        # Add a competition if not already existe
        query = """
        SELECT id FROM competitions WHERE id = %s
        """
        cursor.execute(query, (competition.get('id', None),))
        result = cursor.fetchone()
        if result: 
            return competition.get('id', None)
        query = """
        INSERT INTO competitions
        (id, name, code, type, emblem, area_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (competition.get('id', None), competition.get('name', None), competition.get('code', None), competition.get('type', None), competition.get('emblem', None), area_id))
        connection.commit()
        print('')
        return competition.get('id', None)
    except Exception as e:
        connection.rollback()
        logging.error(f"Error processing competition {competition.get('id', None)}: {e}")
        return None
    
from datetime import datetime

def date_converter(utc_date: str) -> str:
    """
    Converts a UTC date string to MySQL date format (YYYY-MM-DD).
    If the input date is invalid or None, returns an empty string.
    """
    if not utc_date or utc_date == "":
        return None
    try:
        # Parse the UTC date and format it to MySQL date format
        mysql_date = datetime.strptime(utc_date, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")
        return mysql_date
    except (ValueError, TypeError):
        # Handle invalid or None dates
        logging.warning(f"Invalid date format or None value: {utc_date}")
        return None
    
def add_coach_if_not_exist(coach, cursor, connection) -> Union[None, int]:
    """Add coach to MySQL if it does not exist using INSERT INTO."""
    try:
        # Check if coach already exists
        query = """
        SELECT id FROM coaches WHERE id = %s
        """
        cursor.execute(query, (coach.get('id', None),))
        result = cursor.fetchone()
        if result:
            return coach.get('id', None)

        # Insert the coach if not exists
        query = """
        INSERT INTO coaches
        (id, first_name, last_name, name, date_of_birth, nationality, contract_start_date, contract_end_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        mysql_date_of_birth = date_converter(coach.get('date_of_birth', None))
        mysql_contract_start_date = date_converter(coach.get('contract_start_date', None))
        mysql_contract_end_date = date_converter(coach.get('contract_end_date', None))
        cursor.execute(query, (
            coach.get('id', None),
            coach.get('first_name', None), 
            coach.get('last_name', None), 
            coach.get('name', None), 
            mysql_date_of_birth, 
            coach.get('nationality', None), 
            mysql_contract_start_date, 
            mysql_contract_end_date
        ))
        connection.commit()
        return coach.get('id', None)
    except Exception as e:
        connection.rollback()
        logging.error(f"Error processing coach {coach.get('id', None)}: {e}")
        return None

        
def add_area_if_not_exist(area, cursor, connection) -> Union[None, int]:
    """Add area to MySQL if it does not exist using INSERT INTO."""
    """
    AREA MODEL SCHEMA:
    id = 
    name = 
    code = 
    flag = 
    """
    try:
        # Add a area if not already existe
        query = """
        SELECT id FROM areas WHERE id = %s
        """
        cursor.execute(query, (area.get('id', None),))
        result = cursor.fetchone()
        if result:
            return area.get('id', None)
        query = """
        INSERT INTO areas
        (id, name, code, flag)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (area.get('id', None), area.get('name', None), area.get('code', None), area.get('flag', None)))
        connection.commit()
        return area.get('id', None)
    except Exception as e:
        connection.rollback()
        logging.error(f"Error processing area {area.get('id', None)}: {e}")
        return None
    
def add_team_competition_if_not_exist(team_id, competition_id, season, cursor, connection): # doesn't return anything
    """Add team-competition relationship to MySQL if it does not exist using INSERT INTO."""
    """
    TEAM_COMPETITION MODEL SCHEMA:
    id = 
    team_id = 
    competition_id = 
    season = 
    """
    try:
        query = """
        SELECT id FROM team_competitions WHERE team_id = %s AND competition_id = %s AND season = %s
        """
        cursor.execute(query, (team_id, competition_id, season))
        result = cursor.fetchone()
        if result:
            return None
        query = """
        INSERT INTO team_competitions
        (team_id, competition_id, season)
        VALUES (%s, %s, %s)
        """
        cursor.execute(query, (team_id, competition_id, season))
        connection.commit()
    except Exception as e:
        connection.rollback()
        logging.error(f"Error processing team-competition relationship {team_id}-{competition_id}-{season}: {e}")
        
from datetime import datetime

        
def add_player_if_not_exist(player, team_id, cursor, connection) -> Union[None, int]:
    """
    Add player to MySQL if it does not exist using INSERT INTO.

    PLAYER MODEL SCHEMA:
    id = 
    name = 
    position = 
    date_of_birth =
    nationality =
    team =
    """
    try:
        # Check if the player already exists
        query = """
        SELECT id FROM players WHERE id = %s
        """
        cursor.execute(query, (player.get('id', None),))
        result = cursor.fetchone()
        if result:
            return player.get('id', None)


        # Insert the player into the database
        query = """
        INSERT INTO players
        (id, name, position, date_of_birth, nationality, team_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        mysql_date_of_birth = date_converter(player.get('date_of_birth', None))
        cursor.execute(query, (
            player.get('id', None), 
            player.get('name', None), 
            player.get('position', None), 
            mysql_date_of_birth,  # Converted date
            player.get('nationality', None), 
            team_id
        ))
        connection.commit()
        return player.get('id', None)
    except Exception as e:
        connection.rollback()
        logging.error(f"Error processing player {player.get('id', None)}: {e}")
        return None

def add_team_if_not_exist(team, cursor, connection) -> Union[None, int]:
    """Add team to MySQL if it does not exist using INSERT INTO."""
    """
    TEAM MODEL SCHEMA:
    id = 
    name = 
    short_name = 
    tla = 
    crest = 
    address = 
    website = 
    founded = 
    club_colors = 
    venue = 
    area = 
    coach = 
    season = 
    """
    try:
        # null dicts
        area_id = None
        coach_id = None
        # Add a team if not already existe
        query = """
        SELECT id FROM teams WHERE id = %s
        """
        cursor.execute(query, (team.get('id', None),))
        result = cursor.fetchone()
        if result:
            return team.get('id', None)
        query = """
        INSERT INTO teams
        (id, name, short_name, tla, crest, address, website, founded, club_colors, venue, area_id, coach_id, season)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (team.get('id', None), team.get('name', None), team.get('short_name', None), team.get('tla', None), team.get('crest', None), team.get('address', None), team.get('website', None), team.get('founded', None), team.get('club_colors', None), team.get('venue', None), area_id, coach_id, team.get('season', None)))
        connection.commit()
        return team.get('id', None)
    except Exception as e:
        connection.rollback()
        logging.error(f"Error processing team {team.get('id', None)}: {e}")
        return None
    
        

def main():
    """Fetch data from MongoDB and insert into MySQL."""
    try:
        # Connect to MongoDB
        mongo_client = MongoClient(MONGO_URI)
        db = mongo_client[DATABASE_NAME]
        logger.info("Connected to MongoDB.")

        # Connect to MySQL
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        logger.info("Connected to MySQL.")

        # Poll MongoDB for data
        while True:
            # Fetch data from MongoDB collections
            teams_collection = db.teams.find()
            competitions_collection = db.competitions.find()
            matches_collection = db.matches.find()
            top_scorers_collection = db.top_scorers.find()
            standings_collection = db.standings.find()


            if not teams_collection:
                logging.warning(f"No records to process for teams_collection.")
                pass

            if not competitions_collection:
                logging.warning(f"No records to process for competitions.")
                pass

            if not matches_collection:
                logging.warning(f"No records to process for matches.")
                pass

            if not top_scorers_collection:
                logging.warning(f"No records to process for top scorers.")
                pass

            if not standings_collection:
                logging.warning(f"No records to process for standings.")
                pass


            # teams_collection
            logging.info(f"trying to ingest data to mysql teams table: {teams_collection}") 
            
            for teams_list_row in teams_collection:
                season_from_dict = teams_list_row.get("season", None)
                competition_from_dict = teams_list_row.get("competition", {})
                teams = teams_list_row.get("teams", [])  # This is a list of teams

                for team in teams:
                    try:
                        # Safety checks for potential None values
                        team_id = team.get("id", None)
                        team_name = team.get("name", None)
                        team_short_name = team.get("shortName", None)
                        team_tla = team.get("tla", None)
                        team_crest = team.get("crest", None)
                        team_address = team.get("address", None)
                        team_website = team.get("website", None)
                        team_founded = team.get("founded", None)
                        team_club_colors = team.get("clubColors", None)
                        team_venue = team.get("venue", None)

                        # Handle area
                        area = team.get("area")
                        area_id = add_area_if_not_exist(area, cursor, connection) if area else None

                        # Handle season and competitions
                        team_season = team.get("season", season_from_dict)
                        running_competitions = team.get("runningCompetitions", [])

                        team_coach = team.get("coach", None)
                        team_coach_id = add_coach_if_not_exist(team_coach, cursor, connection) if team_coach else None
                        

                        if team_coach_id is None:
                            logging.error(f"Invalid coach_id for team {team.get('id')}. Skipping team insertion.")
                            continue  # Skip this team if no valid coach_id is found


                        # Insert a new team if it doesn't exist
                        query = """
                        SELECT id FROM teams WHERE id = %s
                        """
                        cursor.execute(query, (team_id,))
                        result = cursor.fetchone()
                        if result is None:
                            query = """
                            INSERT INTO teams
                            (id, name, short_name, tla, crest, address, website, founded, club_colors, venue,
                            area_id, coach_id, season)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """
                            cursor.execute(query, (team_id, team_name, team_short_name, team_tla,
                                                team_crest, team_address, team_website, team_founded,
                                                team_club_colors, team_venue, area_id, team_coach_id, team_season))
                         
                        # Process running competitions
                        if running_competitions:
                            for competition in running_competitions:
                                competition_id = add_competition_if_not_exist(competition, area_id, cursor, connection)
                                add_team_competition_if_not_exist(team_id, competition_id, team_season, cursor, connection)
                        else:
                            # Fallback to competition from the dict
                            competition_id = add_competition_if_not_exist(competition_from_dict, area_id, cursor, connection)
                            add_team_competition_if_not_exist(team_id, competition_id, team_season, cursor, connection)

                        connection.commit()
                    except Exception as e:
                        connection.rollback()
                        logging.error(f"Error processing team: {team.get('id', 'unknown')}: {e}")
                    print(f"From teams: {team.get('id', None)}")


            # competitions
            logging.info(f"trying to ingest data to mysql competitions table: {competitions_collection}")
            for competitions_list_row in competitions_collection:
                area = competitions_list_row.get("area", {})
                if area:
                    area_id = add_area_if_not_exist(area, cursor, connection)
                
                competition = {
                    "id": competitions_list_row.get("id", None),
                    "name": competitions_list_row.get("name", None),
                    "code": competitions_list_row.get("code", None),
                    "type": competitions_list_row.get("type", None),
                    "emblem": competitions_list_row.get("emblem", None),
                    "area": area_id if area else None
                }
                
                if competition:
                    competition_id = add_competition_if_not_exist(competition, area_id, cursor, connection)
                print(f"From competitions: {competitions_list_row.get('id', None)}")

                

            # matches
            logging.info(f"trying to ingest data to mysql matches table: {matches_collection}")
            for matches_list_row in matches_collection:
                season_from_dict = matches_list_row.get("season", None)
                competition_from_dict = matches_list_row.get("competition", {})
                matches = matches_list_row.get("matches", [])  # this is a list of matches
                for match in matches:
                    try:
                        # Safety checks for potential None values
                        match_id = match.get("id", None)
                        match_date = match.get("utcDate", None)
                        match_status = match.get("status", None)
                        match_stage = match.get("stage", None)
                        match_home_team = match.get("home_team", {})
                        match_away_team = match.get("away_team", {})
                        match_home_team_score = match.get("score", {}).get("fullTime", {}).get("home", None)
                        match_away_team_score = match.get("score", {}).get("fullTime", {}).get("away", None)

                        area = match.get("area", None)
                        area_id = add_area_if_not_exist(area, cursor, connection) if area else None
                        
                        match_competition = match.get("competition", competition_from_dict)
                        competition_id = add_competition_if_not_exist(match_competition, area_id, cursor, connection) if match_competition else None
                        
                        match_home_team_id = add_team_if_not_exist(match_home_team, cursor, connection) if match_home_team else None
                        match_away_team_id = add_team_if_not_exist(match_away_team, cursor, connection) if match_away_team else None

                        # Now insert the match data
                        query = """
                        INSERT INTO matches
                        (id, match_date, status, stage, home_team_id, away_team_id, home_team_score, away_team_score, area_id, season, competition_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        cursor.execute(query, (match_id, date_converter(match_date), match_status, match_stage, match_home_team_id, match_away_team_id,
                                            match_home_team_score, match_away_team_score, area_id, season_from_dict, competition_id))
                        
                        # cursor.execute(query, (match_id, date_converter(match_date), match_status, match_stage, None, None,
                        #                     match_home_team_score, match_away_team_score, None, season_from_dict, None))

                        connection.commit()
                        # print(f"""
                        #       From matches: {match_id}, {date_converter(match_date)}, {match_status}, {match_stage}, {match_home_team_id}, {match_away_team_id},
                        #         {match_home_team_score}, {match_away_team_score}, {area_id}, {season_from_dict}, {competition_id}
                        #       """)
                    except Exception as e:
                        connection.rollback()
                        logging.error(f"Error processing match {match.get('id', 'unknown')}: {e}")
                    print(f"From matches: {match.get('id', None)}")

                

            # top_scorers
            # logging.info(f"trying to ingest data to mysql top_scorers table: {top_scorers_collection}")
            # for top_scorers_list_row in top_scorers_collection:
            #     season_from_dict = top_scorers_list_row.get("season", None)
            #     competition_from_dict = top_scorers_list_row.get("competition", {})
            #     if competition_from_dict is not None:
            #         competition_id = add_competition_if_not_exist(competition_from_dict, area_id, cursor, connection)
            #     top_scorers = top_scorers_list_row.get("top_scorers", [])  # this is a list of top_scorers
            #     for scorer in top_scorers:
                #     try:
                #         # Safety checks for potential None values
                #         scorer_played_matches = scorer.get("playedMatches", 0)
                #         scorer_goals = scorer.get("goals", 0)
                #         scorer_assists = scorer.get("assists", 0)
                #         scorer_penalties = scorer.get("penalties", 0)
                        
                #         team = scorer.get("team", {})
                #         if team:
                #             team_id = add_team_if_not_exist(team, cursor, connection)
                        
                #         player = scorer.get("player", {})
                #         if player:
                #             player_id = add_player_if_not_exist(player, team_id, cursor, connection)
                            
                #         add_team_competition_if_not_exist(team_id, competition_id, season_from_dict, cursor, connection)

                #         # Update existing scorer
                #         query = """
                #         INSERT INTO top_scorers
                #         (player, team, played_matches, goals, assists, penalties, season, competition)
                #         VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                #         """
                #         cursor.execute(query, (player_id, team_id, scorer_played_matches, scorer_goals, 
                #                             scorer_assists, scorer_penalties, season_from_dict, competition_id))
                        
                #         connection.commit()
                #     except Exception as e:
                #         connection.rollback()
                #         logging.error(f"Error processing scorer {scorer.get('id', 'unknown')}: {e}")
                    # print(f"From top_scorers: {season_from_dict}")
            
            
            # standings
            # logging.info(f"Trying to ingest data to MySQL standings table: {standings_collection}")
            # for standings_list_row in standings_collection:
            #     try:
            #         # Extract season and competition details
            #         season_from_dict = standings_list_row.get("season", None)
            #         competition_from_dict = standings_list_row.get("competition", {})
            #         competition_id = None
            #         if competition_from_dict is not None:
            #             competition_id = add_competition_if_not_exist(competition_from_dict, area_id, cursor, connection)

            #         # Extract area details
            #         area_from_dict = standings_list_row.get("area", None)
            #         if area_from_dict:
            #             area_id = add_area_if_not_exist(area_from_dict, cursor, connection)

            #         # Extract standings list
            #         standings_list = standings_list_row.get("standings", {}).get("standings", [])
            #         standings_tables = [standing.get("table", []) for standing in standings_list if standing]

            #         # Process each standing
            #         for standing_table in standings_tables:
            #             for standing in standing_table:
                            # try:
                            #     # Safety checks for potential None values
                            #     standing_position = standing.get("position", 0)
                            #     standing_played_games = standing.get("playedGames", 0)
                            #     standing_form = standing.get("form", None)
                            #     standing_won = standing.get("won", 0)
                            #     standing_draw = standing.get("draw", 0)
                            #     standing_lost = standing.get("lost", 0)
                            #     standing_points = standing.get("points", 0)
                            #     standing_goals_for = standing.get("goalsFor", 0)
                            #     standing_goals_against = standing.get("goalsAgainst", 0)
                            #     standing_goal_difference = standing.get("goalDifference", 0)

                            #     team = standing.get("team", {})
                            #     if team:
                            #         team_id = add_team_if_not_exist(team, cursor, connection)

                            #     # Update existing standing
                            #     query = """
                            #     INSERT INTO standings
                            #     (team_id, position, played_games, form, won, draw, lost, points, goals_for, goals_against, goal_difference, season, competition_id, area_id)
                            #     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            #     """
                            #     cursor.execute(query, (
                            #         team_id, standing_position, standing_played_games, standing_form, standing_won,
                            #         standing_draw, standing_lost, standing_points, standing_goals_for, standing_goals_against,
                            #         standing_goal_difference, season_from_dict, competition_id, area_id
                            #     ))
                            #     connection.commit()
                            # except Exception as e:
                            #     connection.rollback()
                            #     logging.error(f"Error processing standing: {standing.get('team', {}).get('id', 'unknown')}, Error: {e}")
                #             print(f"From standings: {standing.get('id', None)}")
                # except Exception as e:
                #     logging.error(f"Error processing standings list row: {e}")

            
            logger.info("Waiting for next polling interval...")
            time.sleep(POLLING_INTERVAL)
              

      
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        # Close MongoDB connection
        mongo_client.close()

        # Close MySQL connection
        cursor.close()
        connection.close()
        logger.info("Closed connections.")

if __name__ == '__main__':
  main()