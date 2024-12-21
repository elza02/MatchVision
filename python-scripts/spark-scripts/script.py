from pyspark.sql import SparkSession
from pymongo import MongoClient
import json
from typing import Dict, Any, Union
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
MONGO_URI = "mongodb://root:houcine@mongodb-football-2:27017/"
DATABASE_NAME = "football_data"
KAFKA_BROKER = "kafka:29092"

# Topic configurations
TOPICS = {
    "teams": "teams-topic",
    "competitions": "competitions-topic",
    "matches": "matches-topic",
    "top_scorers": "top-scorers-topic",
    "standings": "standings-topic",
}

def create_spark_session() -> SparkSession:
    """Initialize and return a Spark Session."""
    spark = SparkSession.builder \
        .appName("KafkaToMongoDB") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    return spark

def get_mongo_client() -> MongoClient:
    """Create and return a MongoDB client."""
    return MongoClient(MONGO_URI)

def normalize_document(doc: Any, topic: str) -> Union[Dict, None]:
    """Normalize document based on topic type."""
    try:
        if isinstance(doc, str):
            doc = json.loads(doc)
        
        if isinstance(doc, list):
            # Handle array data differently based on topic
            if topic == "competitions":
                return {"competitions": doc}
            else:
                return {"data": doc}
        
        elif isinstance(doc, dict):
            return doc
        
        else:
            logger.error(f"Unsupported document type for topic {topic}: {type(doc)}")
            return None
            
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse document as JSON for topic {topic}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error normalizing document for topic {topic}: {e}")
        return None

def save_to_mongo(data: list, collection_name: str, db) -> None:
    """Save normalized data to MongoDB."""
    if not data:
        logger.warning(f"No data to save to MongoDB for collection {collection_name}")
        return

    collection = db[collection_name]
    valid_documents = []
    
    for record in data:
        normalized_doc = normalize_document(record, collection_name)
        if normalized_doc:
            valid_documents.append(normalized_doc)
            logger.debug(f"Normalized document for {collection_name}: {normalized_doc}")
    
    if valid_documents:
        try:
            collection.insert_many(valid_documents)
            logger.info(f"Successfully inserted {len(valid_documents)} documents into {collection_name}")
        except Exception as e:
            logger.error(f"Bulk insert failed for {collection_name}: {e}")
            # Fallback to individual inserts
            for doc in valid_documents:
                try:
                    collection.insert_one(doc)
                except Exception as e:
                    logger.error(f"Failed to insert document into {collection_name}: {e}")
    else:
        logger.warning(f"No valid documents to insert into {collection_name}")

def process_stream(df, epoch_id, collection_name: str, db) -> None:
    """Process each micro-batch of Kafka stream."""
    try:
        json_strings = df.selectExpr("CAST(value AS STRING) AS json_string") \
                        .select("json_string") \
                        .rdd \
                        .map(lambda row: row.json_string) \
                        .collect()
        
        logger.info(f"Processing batch with {len(json_strings)} messages for {collection_name}")
        
        parsed_data = []
        for json_string in json_strings:
            try:
                if json_string and json_string.strip():
                    parsed_record = json.loads(json_string)
                    parsed_data.append(parsed_record)
                    logger.debug(f"Successfully parsed record for {collection_name}")
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error in {collection_name}: {e}, Data: {json_string[:100]}...")
        
        if parsed_data:
            save_to_mongo(parsed_data, collection_name, db)
        else:
            logger.warning(f"No valid data parsed from batch for {collection_name}")
            
    except Exception as e:
        logger.error(f"Error processing batch for {collection_name}: {e}")

def create_stream(spark: SparkSession, topic: str, collection_name: str, db) -> None:
    """Create and start a stream for a specific topic."""
    try:
        logger.info(f"Starting stream for topic: {topic}")
        
        kafka_df = spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", KAFKA_BROKER) \
            .option("subscribe", topic) \
            .load()
        
        query = kafka_df.writeStream \
            .foreachBatch(lambda df, epoch_id: process_stream(df, epoch_id, collection_name, db)) \
            .start()
        
        return query
    
    except Exception as e:
        logger.error(f"Error creating stream for topic {topic}: {e}")
        raise

def main():
    """Main execution function."""
    try:
        # Initialize Spark and MongoDB
        spark = create_spark_session()
        mongo_client = get_mongo_client()
        db = mongo_client[DATABASE_NAME]
        
        # Create streams for all topics
        queries = []
        for collection_name, topic in TOPICS.items():
            query = create_stream(spark, topic, collection_name, db)
            queries.append(query)
        
        logger.info("All streams started successfully")
        
        # Wait for all queries to terminate
        for query in queries:
            query.awaitTermination()
        
    except Exception as e:
        logger.error(f"Application error: {e}")
    finally:
        if 'mongo_client' in locals():
            mongo_client.close()
            logger.info("MongoDB connection closed")

if __name__ == "__main__":
    main()