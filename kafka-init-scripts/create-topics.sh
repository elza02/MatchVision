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
