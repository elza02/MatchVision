#!/bin/sh

echo "Waiting for Kafka to be ready..."
sleep 10

echo "Creating Kafka topics..."
kafka-topics --create --if-not-exists --bootstrap-server kafka:29092 --topic teams-topic --partitions 1 --replication-factor 1
kafka-topics --create --if-not-exists --bootstrap-server kafka:29092 --topic competitions-topic --partitions 1 --replication-factor 1
kafka-topics --create --if-not-exists --bootstrap-server kafka:29092 --topic matches-topic --partitions 1 --replication-factor 1
kafka-topics --create --if-not-exists --bootstrap-server kafka:29092 --topic top-scorers-topic --partitions 1 --replication-factor 1
kafka-topics --create --if-not-exists --bootstrap-server kafka:29092 --topic player-stats-topic --partitions 1 --replication-factor 1
kafka-topics --create --if-not-exists --bootstrap-server kafka:29092 --topic match-predictions-topic --partitions 1 --replication-factor 1
kafka-topics --create --if-not-exists --bootstrap-server kafka:29092 --topic team-formations-topic --partitions 1 --replication-factor 1
kafka-topics --create --if-not-exists --bootstrap-server kafka:29092 --topic betting-odds-topic --partitions 1 --replication-factor 1

echo "Listing created topics:"
kafka-topics --list --bootstrap-server kafka:29092
#!/bin/sh

echo "Waiting for Kafka to be ready..."
while ! nc -z kafka 29092; do   
  sleep 1
done
echo "Kafka is ready."

BOOTSTRAP_SERVER=${BOOTSTRAP_SERVER:-kafka:29092}
topics=("teams-topic" "competitions-topic" "matches-topic" "top-scorers-topic" 
        "player-stats-topic" "match-predictions-topic" "team-formations-topic" "betting-odds-topic")

for topic in "${topics[@]}"; do
  echo "Creating topic: $topic..."
  kafka-topics --create --if-not-exists --bootstrap-server "$BOOTSTRAP_SERVER" --topic "$topic" --partitions 1 --replication-factor 1 || {
    echo "Failed to create $topic" >&2
    exit 1
  }
done

echo "Listing created topics:"
kafka-topics --list --bootstrap-server "$BOOTSTRAP_SERVER"
