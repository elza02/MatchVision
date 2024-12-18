from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DateType
from pyspark.sql.functions import col, from_json, regexp_replace, to_timestamp, trim
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError
import mysql.connector
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

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
            admin_client.create_topics(new_topics=topics_to_create, validate_only=True)
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

def check_foreign_key_exists(cursor, table, column, value):
    """
    Check if a foreign key value exists in the referenced table
    """
    if value is None:
        return True
    
    try:
        cursor.execute(f"SELECT 1 FROM {table} WHERE id = %s", (value,))
        return cursor.fetchone() is not None
    except Exception as e:
        logging.error(f"Error checking foreign key in {table}: {e}")
        return True


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

        if not records:
            logging.warning(f"No records to process for {table_name}")
            return

        if table_name == "teams":
            logging.info(f"trying to ingest data to mysql teams table: {records}") 
            for row in records:
                try:
                    cursor.execute("SELECT id FROM teams WHERE id = %s", (row.id,))
                    team_exists = cursor.fetchone()

                    # Safety checks for potential None values
                    founded = row.founded if row.founded is not None else None
                    website = row.website if row.website is not None else ""
                    crest = row.crest if row.crest is not None else ""
                    club_colors = row.club_colors if row.club_colors is not None else ""
                    venue = row.venue if row.venue is not None else ""

                    if team_exists:
                        # Update existing team
                        query = """
                        UPDATE teams
                        SET name = %s, competition_name = %s, crest = %s, website = %s, founded = %s,
                        club_colors = %s, venue = %s
                        WHERE id = %s
                        """
                        cursor.execute(query, (row.name, row.competition_name, row.crest, row.website, 
                                               row.founded, row.club_colors, row.venue, row.id))
                    else:
                        # Insert new team
                        query = """
                        INSERT INTO teams 
                        (id, name, competition_name, crest, website, founded, club_colors, venue)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        cursor.execute("SELECT id FROM competitions WHERE name = %s", (row.competition,))
                        competition = cursor.fetchone()
                        if competition:
                            cursor.execute(query, (row.id, row.name, row.competition_name, row.crest, row.website,
                                                    row.founded, row.club_colors, row.venue))
                        else:
                            logging.warning(f"Competition {row.competition} not found for team {row.name}")
                    
                    connection.commit()
                except Exception as e:
                    connection.rollback()
                    logging.error(f"Error processing team {row.id}: {e}")

        elif table_name == "competitions":
            logging.info(f"trying to ingest data to mysql competitions table: {records}") 
            for row in records:
                try:
                    cursor.execute("SELECT id FROM competitions WHERE id = %s", (row.id,))
                    competition_exists = cursor.fetchone()
                    
                    # fake_data_if_exist = ("name1", "area1", "code1", "type1", "emblem1", 1)
                    # fake_data_if_not_exist = (1, "name1", "area1", "code1", "type1", "emblem1")

                    if competition_exists:
                        # Update existing competition
                        query = """
                        UPDATE competitions
                        SET name = %s, area = %s, code = %s, type = %s, emblem = %s
                        WHERE id = %s
                        """
                        cursor.execute(query, (row.name, row.area, row.code, row.type, row.emblem, row.id))
                        # cursor.execute(query, fake_data_if_exist)
                        # logging.info(f"data to ingest into mysql competitions table: {fake_data_if_exist}")
                    else:
                        # Insert new competition
                        query = """
                        INSERT INTO competitions (id, name, area, code, type, emblem)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """
                        cursor.execute(query, (row.id, row.name, row.area, row.code, row.type, row.emblem))
                        # cursor.execute(query, fake_data_if_not_exist)
                        # logging.info(f"data to ingest into mysql competitions table: {fake_data_if_not_exist}")
                    connection.commit()
                except Exception as e:
                    connection.rollback()
                    logging.error(f"Error processing competition {row.id}: {e}")

        elif table_name == "matches":
            logging.info(f"trying to ingest data to mysql matches table: {records}") 
            for row in records:
                try:
                    query = """
                    REPLACE INTO matches 
                    (id, competition_id, season, home_team_id, away_team_id, 
                    match_date, status, home_team_score, away_team_score, referee)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    data = (
                        row.id,
                        row.competition_id,
                        row.season,
                        row.home_team_id,
                        row.away_team_id,
                        row.match_date or None,
                        row.status or '',
                        int(row.home_team_score or 0),
                        int(row.away_team_score or 0),
                        row.referee or ''
                    )
                    cursor.execute(query, data)
                    connection.commit()
                except Exception as e:
                    connection.rollback()
                    logging.error(f"Error processing match {row.id}: {e}")

        elif table_name == "top_scorers":
            for row in records:
                try:
                    query = """
                    REPLACE INTO top_scorers 
                    (player_id, player_name, team_id, competition_id, season,
                    goals, assists, played_matches, penalties)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    data = (
                        row.player_id,
                        row.player_name,
                        row.team_id,
                        row.competition_id,
                        row.season,
                        int(row.goals or 0),
                        int(row.assists or 0),
                        int(row.played_matches or 0),
                        int(row.penalties or 0)
                    )
                    cursor.execute(query, data)
                    connection.commit()
                except Exception as e:
                    connection.rollback()
                    logging.error(f"Error processing top scorer {row.player_id}: {e}")

        elif table_name == "player_stats":
            for row in records:
                try:
                    query = """
                    REPLACE INTO player_stats 
                    (player_id, name, position, goals, assists, 
                    minutes_played, team_id, match_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    data = (
                        row.player_id,
                        row.name or '',
                        row.position or '',
                        int(row.goals or 0),
                        int(row.assists or 0),
                        int(row.minutes_played or 0),
                        row.team_id,
                        row.match_id
                    )
                    cursor.execute(query, data)
                    connection.commit()
                except Exception as e:
                    connection.rollback()
                    logging.error(f"Error processing player stats for {row.player_id}: {e}")

        elif table_name == "match_predictions":
            for row in records:
                try:
                    query = """
                    REPLACE INTO match_predictions 
                    (match_id, home_team_win_prob, draw_prob, 
                    away_team_win_prob, predicted_score)
                    VALUES (%s, %s, %s, %s, %s)
                    """
                    data = (
                        row.match_id,
                        float(row.home_team_win_prob or 0.0),
                        float(row.draw_prob or 0.0),
                        float(row.away_team_win_prob or 0.0),
                        row.predicted_score or ''
                    )
                    cursor.execute(query, data)
                    connection.commit()
                except Exception as e:
                    connection.rollback()
                    logging.error(f"Error processing match prediction for {row.match_id}: {e}")

        elif table_name == "team_formations":
            for row in records:
                try:
                    query = """
                    REPLACE INTO team_formations 
                    (match_id, team_id, formation, players)
                    VALUES (%s, %s, %s, %s)
                    """
                    data = (
                        row.match_id,
                        row.team_id,
                        row.formation or '',
                        row.players or ''
                    )
                    cursor.execute(query, data)
                    connection.commit()
                except Exception as e:
                    connection.rollback()
                    logging.error(f"Error processing team formation for {row.match_id}: {e}")

        elif table_name == "betting_odds":
            for row in records:
                try:
                    query = """
                    REPLACE INTO betting_odds 
                    (match_id, home_win_odds, draw_odds, away_win_odds)
                    VALUES (%s, %s, %s, %s)
                    """
                    data = (
                        row.match_id,
                        float(row.home_win_odds or 0.0),
                        float(row.draw_odds or 0.0),
                        float(row.away_win_odds or 0.0)
                    )
                    cursor.execute(query, data)
                    connection.commit()
                except Exception as e:
                    connection.rollback()
                    logging.error(f"Error processing betting odds for match {row.match_id}: {e}")


    except mysql.connector.Error as mysql_err:
        logging.error(f"MySQL Connection Error: {mysql_err}")
    except Exception as e:
        logging.error(f"Unexpected error in save_to_mysql: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# Define Kafka schema for topics
schemas = {
    "teams": StructType([
        StructField("id", IntegerType(), True),
        StructField("name", StringType(), True),
        StructField("competition_name", StringType(), True),
        StructField("crest", StringType(), True),
        StructField("website", StringType(), True),
        StructField("founded", StringType(), True),
        StructField("club_colors", StringType(), True),
        StructField("venue", StringType(), True)
    ]),
    "competitions": StructType([
        StructField("id", IntegerType(), True),
        StructField("name", StringType(), True),
        StructField("area", StringType(), True),
        StructField("code", StringType(), True),
        StructField("type", StringType(), True),
        StructField("emblem", StringType(), True)
    ]),
    "matches": StructType([
        StructField("id", IntegerType(), True),
        StructField("competition_id", IntegerType(), True),
        StructField("season", IntegerType(), True),
        StructField("match_date", StringType(), True),
        StructField("status", StringType(), True),
        StructField("home_team_id", IntegerType(), True),
        StructField("away_team_id", IntegerType(), True),
        StructField("home_team_score", IntegerType(), True),
        StructField("away_team_score", IntegerType(), True),
        StructField("referee", StringType(), True)
    ]),
    "top_scorers": StructType([
        StructField("player_id", IntegerType(), True),
        StructField("player_name", StringType(), True),
        StructField("team_id", IntegerType(), True),
        StructField("competition_id", IntegerType(), True),
        StructField("season", IntegerType(), True),
        StructField("goals", IntegerType(), True),
        StructField("assists", IntegerType(), True),
        StructField("played_matches", IntegerType(), True),
        StructField("penalties", IntegerType(), True)
    ]),
    "player_stats": StructType([
        StructField("player_id", IntegerType(), True),
        StructField("name", StringType(), True),
        StructField("position", StringType(), True),
        StructField("goals", IntegerType(), True),
        StructField("assists", IntegerType(), True),
        StructField("minutes_played", IntegerType(), True),
        StructField("team_id", IntegerType(), True),
        StructField("match_id", IntegerType(), True)
    ]),
    "match_predictions": StructType([
        StructField("match_id", IntegerType(), True),
        StructField("home_team_win_prob", StringType(), True),
        StructField("draw_prob", StringType(), True),
        StructField("away_team_win_prob", StringType(), True),
        StructField("predicted_score", StringType(), True)
    ]),
    "team_formations": StructType([
        StructField("match_id", IntegerType(), True),
        StructField("team_id", IntegerType(), True),
        StructField("formation", StringType(), True),
        StructField("players", StringType(), True)
    ]),
    "betting_odds": StructType([
        StructField("match_id", IntegerType(), True),
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
        .option("failOnDataLoss", "True") \
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

    # Debugging: Show parsed data in the console if table name is competitions
    if table_name == "competitions":
        parsed_df.writeStream \
            .outputMode("append") \
            .format("console") \
            .start()
            


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
        
    for table_name, topic_name in TOPICS.items():
        # some loggings
        logging.info(f"Processing Kafka topic {topic_name} for table {table_name}")
        process_kafka_topic(topic_name, table_name)

    spark.streams.awaitAnyTermination()
    
    
    