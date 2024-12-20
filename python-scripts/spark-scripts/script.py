from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pymongo import MongoClient
import json

# Configuration MongoDB
MONGO_URI = "mongodb://root:houcine@mongodb-football-2:27017/"
DATABASE_NAME = "football_data"

# Configuration Kafka
KAFKA_BROKER = "kafka:29092"
TOPICS = {
    "teams": "teams-topic",
    "competitions": "competitions-topic",
    "matches": "matches-topic",
    "top_scorers": "top-scorers-topic",
    "standings": "standings-topic",
}

# Initialiser la session Spark
spark = SparkSession.builder \
    .appName("KafkaToMongoDB") \
    .getOrCreate()

spark.sparkContext.setLogLevel("OFF")

# Client MongoDB
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DATABASE_NAME]

def save_to_mongo(data, collection_name):
    """Enregistrer les données JSON dans MongoDB."""
    collection = db[collection_name]
    for record in data:
        try:
            collection.insert_one(record)
        except Exception as e:
            print(f"Erreur lors de l'enregistrement dans MongoDB: {e}")

def process_stream(df, topic_name):
    """Traiter chaque micro-lot de flux Kafka."""
    # Lire les données en tant que chaîne JSON
    data = df.selectExpr("CAST(value AS STRING) AS json_string")
    
    # Collecter les données JSON sans schéma
    json_data = data.toJSON().map(lambda x: json.loads(x)).collect()
    
    # Enregistrer dans MongoDB
    save_to_mongo(json_data, topic_name)

# Lire depuis Kafka et traiter chaque sujet
for topic, kafka_topic in TOPICS.items():
    print(f"Démarrage du flux pour le sujet: {topic}")
    kafka_df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BROKER) \
        .option("subscribe", kafka_topic) \
        .load()

    query = kafka_df.writeStream \
        .foreachBatch(lambda df, _: process_stream(df, topic)) \
        .start()

    query.awaitTermination()

# Arrêter le client MongoDB après la fin
mongo_client.close()
