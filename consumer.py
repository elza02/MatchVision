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
        if message.value:
            # Successfully deserialized JSON data
            print("Received message:", message.value)
        else:
            print("Empty message received, skipping.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
