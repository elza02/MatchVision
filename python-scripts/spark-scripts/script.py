from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DateType
from pyspark.sql.functions import col, from_json, regexp_replace, to_timestamp, trim
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError
import mysql.connector
import logging

# Kafka and MySQL Configuration
KAFKA_BROKER = "kafka:29092"  
DB_CONFIG = {
    'host': 'mysql-football-2',
    'user': 'houcine',
    'password': 'houcine',
    'database': 'football_2'
}

TOPICS = {
    "teams": "teams-topic",
    "competitions": "competitions-topic",
    "matches": "matches-topic",
    "top_scorers": "top-scorers-topic",
    "player_stats": "player-stats-topic",
    "match_predictions": "match-predictions-topic",
    "team_formations": "team-formations-topic",
    "betting_odds": "betting-odds-topic"
}

# Kafka Admin Functionality
def ensure_kafka_topics(broker, topics):
    """
    Ensure that the Kafka topics exist; create them if they do not.
    """
    admin_client = KafkaAdminClient(bootstrap_servers=broker)
    existing_topics = admin_client.list_topics()
    topics_to_create = []

    for topic in topics.values():
        if topic not in existing_topics:  
            topics_to_create.append(NewTopic(name=topic, num_partitions=1, replication_factor=1))

    if topics_to_create:
        try:
            admin_client.create_topics(new_topics=topics_to_create, validate_only=False)
            logging.info(f"Created topics: {[topic.name for topic in topics_to_create]}")
        except TopicAlreadyExistsError:
            logging.warning("Some topics already exist. Skipping creation.")
        except Exception as e:
            logging.error(f"Error creating topics: {e}")
    else:
        logging.info("All topics already exist.")

    admin_client.close()
  
# Ensure Kafka topics exist
ensure_kafka_topics(KAFKA_BROKER, TOPICS)

# Spark Session Initialization
spark = SparkSession.builder \
    .appName("Football Data Consumer") \
    .getOrCreate()

# Set log level to ERROR to reduce logging output
spark.sparkContext.setLogLevel("WARN")

# Save DataFrame to MySQL
def check_foreign_key_exists(cursor, table, field, value):
    """Helper function to check if a foreign key exists"""
    cursor.execute(f"SELECT id FROM {table} WHERE id = %s", (value,))
    return cursor.fetchone() is not None

import mysql.connector
import logging

# Assuming DB_CONFIG is defined elsewhere in your code
# from your_config import DB_CONFIG

def check_foreign_key_exists(cursor, table, field, value):
    """Helper function to check if a foreign key exists"""
    cursor.execute(f"SELECT id FROM {table} WHERE id = %s", (value,))
    return cursor.fetchone() is not None

def save_to_mysql(df, table_name, epoch_id):
    """
    Save the given DataFrame to MySQL with enhanced error handling and logging
    """
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        records = df.collect()

        if table_name == "teams":
            # For teams, we need to check if they're referenced before updating
            for row in records:
                # Check if team exists
                cursor.execute("SELECT id FROM teams WHERE id = %s", (row.id,))
                team_exists = cursor.fetchone()

                if team_exists:
                    # Update existing team without affecting relationships
                    query = """
                    UPDATE teams
                    SET name = %s, crest = %s, website = %s, founded = %s, club_colors = %s, venue = %s
                    WHERE id = %s
                    """
                    cursor.execute(query, (row.name, row.crest, row.website, row.founded, row.club_colors, row.venue, row.id))
                else:
                    # Insert new team
                    query = """
                    INSERT INTO teams (id, name, competition, crest, website, founded, club_colors, venue)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute("SELECT id FROM competitions WHERE name = %s", (row.competition,))
                    competition = cursor.fetchone()
                    if competition:
                        cursor.execute(query, (row.id, row.name, row.competition, row.crest, row.website, row.founded, row.club_colors, row.venue))
                    else:
                        logging.warning(f"Competition {row.competition} not found for team {row.name}. Skipping insertion.")
                connection.commit()
            return

        # Check foreign key dependencies for other tables
        if table_name in ["matches", "top_scorers"]:
            valid_records = []
            for row in records:
                is_valid = True

                # Check team dependencies
                team_ids = []
                if table_name == "matches":
                    team_ids = [row.home_team_id, row.away_team_id]
                elif table_name == "top_scorers":
                    team_ids = [row.team_id]

                for team_id in team_ids:
                    if not check_foreign_key_exists(cursor, "teams", "id", team_id):
                        logging.warning(f"Team with ID {team_id} not found. Skipping record.")
                        is_valid = False
                        break

                # Check competition dependency
                if hasattr(row, 'competition_id') and not check_foreign_key_exists(cursor, "competitions", "id", row.competition_id):
                    logging.warning(f"Competition with ID {row.competition_id} not found. Skipping record.")
                    is_valid = False

                if is_valid:
                    valid_records.append(row)

            records = valid_records

        if not records:
            logging.warning(f"No valid records to insert for {table_name}")
            return

        # Prepare the query and data based on table_name
        if table_name == "competitions":
            for row in records:
                # Check if competition exists
                cursor.execute("SELECT id FROM competitions WHERE id = %s", (row.id,))
                competition_exists = cursor.fetchone()

                if competition_exists:
                    # Update existing competition without affecting relationships
                    query = """
                    UPDATE competitions
                    SET name = %s, area = %s, code = %s, type = %s, emblem = %s
                    WHERE id = %s
                    """
                    cursor.execute(query, (row.name, row.area, row.code, row.type, row.emblem, row.id))
                else:
                    # Insert new competition
                    query = """
                    INSERT INTO competitions (id, name, area, code, type, emblem)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(query, (row.id, row.name, row.area, row.code, row.type, row.emblem))
                connection.commit()

        elif table_name == "matches":
            query = """
            REPLACE INTO matches (id, competition_id, season, home_team_id, away_team_id,
            match_date, status, home_team_score, away_team_score, referee)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            data = []
            for row in records:
                try:
                    data.append((
                        row.id,
                        row.competition_id,
                        row.season,
                        row.home_team_id,
                        row.away_team_id,
                        row.match_date,
                        row.status,
                        int(row.home_team_score or 0),
                        int(row.away_team_score or 0),
                        row.referee
                    ))
                except Exception as e:
                    logging.error(f"Error processing match record: {e}")
                    continue

        elif table_name == "top_scorers":
            query = """
            REPLACE INTO top_scorers (player_id, player_name, team_id, competition_id, season,
            goals, assists, played_matches)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            data = []
            for row in records:
                try:
                    data.append((
                        row.player_id,
                        row.player_name,
                        row.team_id,
                        row.competition_id,
                        row.season,
                        int(row.goals or 0),
                        int(row.assists or 0),
                        int(row.played_matches or 0)
                    ))
                except Exception as e:
                    logging.error(f"Error processing top scorer record: {e}")
                    continue

        elif table_name == "player_stats":
            query = """
            REPLACE INTO player_stats 
            (player_id, name, position, goals, assists, minutes_played, team_id, match_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            data = [
                (row.player_id, row.name, row.position, 
                 row.goals or 0, row.assists or 0, row.minutes_played or 0,
                 row.team_id, row.match_id) 
                for row in records
            ]

        elif table_name == "match_predictions":
            query = """
            REPLACE INTO match_predictions 
            (match_id, home_team_win_prob, draw_prob, away_team_win_prob, predicted_score)
            VALUES (%s, %s, %s, %s, %s)
            """
            data = [
                (row.match_id, 
                 row.home_team_win_prob or 0.0, 
                 row.draw_prob or 0.0, 
                 row.away_team_win_prob or 0.0, 
                 row.predicted_score) 
                for row in records
            ]

        elif table_name == "team_formations":
            query = """
            REPLACE INTO team_formations 
            (match_id, team_id, formation, players)
            VALUES (%s, %s, %s, %s)
            """
            data = [
                (row.match_id, row.team_id, row.formation, row.players) 
                for row in records
            ]

        elif table_name == "betting_odds":
            query = """
            REPLACE INTO betting_odds 
            (match_id, home_win_odds, draw_odds, away_win_odds, timestamp)
            VALUES (%s, %s, %s, %s, %s)
            """
            data = [
                (row.match_id, 
                 row.home_win_odds or 0.0, 
                 row.draw_odds or 0.0, 
                 row.away_win_odds or 0.0, 
                 row.timestamp) 
                for row in records
            ]

        if data:
            try:
                cursor.executemany(query, data)
                connection.commit()
                logging.info(f"Successfully saved {len(data)} records to {table_name}")
            except mysql.connector.Error as err:
                connection.rollback()
                logging.error(f"Error executing MySQL query: {err}")
                raise
        else:
            logging.warning(f"No valid data to insert for {table_name}")

    except mysql.connector.Error as err:
        logging.error(f"MySQL Error: {err}")
        if connection:
            connection.rollback()
        raise
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        if connection:
            connection.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# Define Kafka schema for topics
schemas = {
    "teams": StructType([
        StructField("id", IntegerType(), False),
        StructField("name", StringType(), False),
        StructField("competition", StringType(), False),
        StructField("crest", StringType(), True),
        StructField("website", StringType(), True),
        StructField("founded", StringType(), True),
        StructField("club_colors", StringType(), True),
        StructField("venue", StringType(), True)
    ]),
    "competitions": StructType([
        StructField("id", IntegerType(), False),
        StructField("name", StringType(), False),
        StructField("area", StringType(), True),
        StructField("code", StringType(), True),
        StructField("type", StringType(), True),
        StructField("emblem", StringType(), True)
    ]),
    "matches": StructType([
        StructField("id", IntegerType(), False),
        StructField("competition_id", IntegerType(), False),
        StructField("season", IntegerType(), False),
        StructField("match_date", StringType(), True),
        StructField("status", StringType(), True),
        StructField("home_team_id", IntegerType(), True),
        StructField("away_team_id", IntegerType(), True),
        StructField("home_team_score", IntegerType(), True),
        StructField("away_team_score", IntegerType(), True),
        StructField("referee", StringType(), True)
    ]),
    "top_scorers": StructType([
        StructField("player_id", IntegerType(), False),
        StructField("player_name", StringType(), False),
        StructField("team_id", IntegerType(), False),
        StructField("competition_id", IntegerType(), False),
        StructField("season", IntegerType(), False),
        StructField("goals", IntegerType(), False),
        StructField("assists", IntegerType(), True),
        StructField("played_matches", IntegerType(), True),
        StructField("penalties", IntegerType(), True)
    ]),
    "player_stats": StructType([
        StructField("player_id", IntegerType(), False),
        StructField("name", StringType(), True),
        StructField("position", StringType(), True),
        StructField("goals", IntegerType(), True),
        StructField("assists", IntegerType(), True),
        StructField("minutes_played", IntegerType(), True),
        StructField("team_id", IntegerType(), True),
        StructField("match_id", IntegerType(), True)
    ]),
    "match_predictions": StructType([
        StructField("match_id", IntegerType(), False),
        StructField("home_team_win_prob", StringType(), True),
        StructField("draw_prob", StringType(), True),
        StructField("away_team_win_prob", StringType(), True),
        StructField("predicted_score", StringType(), True)
    ]),
    "team_formations": StructType([
        StructField("match_id", IntegerType(), False),
        StructField("team_id", IntegerType(), False),
        StructField("formation", StringType(), True),
        StructField("players", StringType(), True)
    ]),
    "betting_odds": StructType([
        StructField("match_id", IntegerType(), False),
        StructField("home_win_odds", StringType(), True),
        StructField("draw_odds", StringType(), True),
        StructField("away_win_odds", StringType(), True),
        StructField("timestamp", StringType(), True)
    ])
}

from datetime import datetime

from pyspark.sql.functions import udf
from pyspark.sql.types import StringType
from datetime import datetime


# UDF for date conversion
@udf(StringType())
def convert_utc_to_mysql_datetime_udf(utc_date):
    """
    UDF to convert UTC date string to MySQL DATETIME format.
    """
    if utc_date is None:
        return None
    try:
        date_obj = datetime.strptime(utc_date, "%Y-%m-%dT%H:%M:%SZ")
        return date_obj.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        print(f"Error converting date: {e}")
        return None


def process_kafka_topic(topic_name, table_name):
    """
    Process a specific Kafka topic and save its data to MySQL.
    """
    # Read data from Kafka
    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BROKER) \
        .option("subscribe", topic_name) \
        .load()

    # Parse the Kafka messages into structured data
    parsed_df = df.select(
        from_json(col("value").cast("string"), schemas[table_name]).alias("data")
    ).select("data.*")

    # Transform date columns if required
    if "match_date" in parsed_df.columns:
        parsed_df = parsed_df.withColumn(
            "match_date", convert_utc_to_mysql_datetime_udf(col("match_date"))
        )

    # Validate data
    if table_name == "player_stats":
        parsed_df = validate_player_stats(parsed_df)
    elif table_name == "match_predictions":
        parsed_df = validate_match_predictions(parsed_df)

    # Save data to MySQL
    parsed_df.writeStream \
        .foreachBatch(lambda batch_df, epoch_id: save_to_mysql(batch_df, table_name, epoch_id)) \
        .start()

    # Debugging: Show parsed data in the console
    # parsed_df.writeStream \
    #     .format("console") \
    #     .start()


def validate_player_stats(df):
    """Validate player statistics data"""
    return df.filter(
        (col("goals") >= 0) & 
        (col("assists") >= 0) & 
        (col("minutes_played") >= 0) &
        col("player_id").isNotNull() &
        col("team_id").isNotNull()
    )

def validate_match_predictions(df):
    """Validate match prediction probabilities"""
    return df.filter(
        col("match_id").isNotNull() &
        (col("home_team_win_prob") >= 0) &
        (col("home_team_win_prob") <= 1) &
        (col("draw_prob") >= 0) &
        (col("draw_prob") <= 1) &
        (col("away_team_win_prob") >= 0) &
        (col("away_team_win_prob") <= 1)
    )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('football_analytics.log'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)

    for table_name, topic_name in TOPICS.items():
        process_kafka_topic(topic_name, table_name)

    spark.streams.awaitAnyTermination()
