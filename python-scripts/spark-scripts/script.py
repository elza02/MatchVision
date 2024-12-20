from pyspark.sql import SparkSession
from pyspark.sql.types import StringType
from pyspark.sql.functions import from_json, col
from pymongo import MongoClient
import json

# MongoDB Configuration
MONGO_URI = "mongodb://root:houcine@mongodb-football-2:27017/"
DATABASE_NAME = "football_data"

# Kafka Configuration
KAFKA_BROKER = "kafka:29092"
TOPICS = {
    "teams": "teams-topic",
    "competitions": "competitions-topic",
    "matches": "matches-topic",
    "top_scorers": "top-scorers-topic",
    "standings": "standings-topic",
}

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("KafkaToMongoDB") \
    .getOrCreate()

spark.sparkContext.setLogLevel("OFF")

# MongoDB Client
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DATABASE_NAME]

def save_to_mongo(data, collection_name):
    """Save parsed JSON data to MongoDB."""
    collection = db[collection_name]
    for record in data:
        try:
            collection.insert_one(record)
        except Exception as e:
            print(f"Error saving to MongoDB: {e}")

def process_stream(df, topic_name):
    """Process each micro-batch of Kafka stream."""
    data = df.selectExpr("CAST(value AS STRING)") \
             .withColumn("json_data", from_json(col("value"), StringType())) \
             .select("json_data.*")
    
    # Collect and save to MongoDB
    json_data = data.toJSON().map(lambda x: json.loads(x)).collect()
    save_to_mongo(json_data, topic_name)

# Read from Kafka and process each topic
for topic, kafka_topic in TOPICS.items():
    print(f"Starting stream for topic: {topic}")
    kafka_df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BROKER) \
        .option("subscribe", kafka_topic) \
        .load()

    query = kafka_df.writeStream \
        .foreachBatch(lambda df, _: process_stream(df, topic)) \
        .start()

    query.awaitTermination()

# Stop MongoDB client after completion
mongo_client.close()
