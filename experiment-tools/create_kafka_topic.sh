#!/bin/bash

USAGE="Usage: create_kafka_topic.sh (kafka_ip) (topic_name)"

# create a random topic
KAFKAIP=$1
TOPICNAME=$2
printf 'kafkaip: %s topic_name: %s\n' "$KAFKAIP" "$TOPICNAME"

# create topic in kafka
ssh "ubuntu@$KAFKAIP" "cd kafka/ && bin/kafka-topics.sh --create --topic "$TOPICNAME" --bootstrap-server "$KAFKAIP":9092"
