from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType, IntegerType

# Create Spark session
spark = SparkSession.builder.appName("PremierLeagueStreamApp").getOrCreate()

# Define the schema of match data
match_schema = StructType() \
    .add("home_team", StringType()) \
    .add("away_team", StringType()) \
    .add("home_score", IntegerType()) \
    .add("away_score", IntegerType()) \
    .add("match_date", StringType())

# Read from Kafka topic
df = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "premier_league_results") \
    .load()

# Convert Kafka value from bytes to JSON
df = df.selectExpr("CAST(value AS STRING)")

# Parse the JSON data
match_data = df.select(from_json(col("value"), match_schema).alias("match"))

# Select the necessary fields
processed_data = match_data.select("match.home_team", "match.away_team", "match.home_score", "match.away_score", "match.match_date")

# Write to console (can be replaced by writing to a database or dashboard)
query = processed_data.writeStream.outputMode("append").format("console").start()

query.awaitTermination()
