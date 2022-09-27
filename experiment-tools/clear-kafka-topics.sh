#!/bin/bash
# scp this file to kafka machine cd kafka/
# ssh to kafka machine and sh this file
USAGE="Usage: clear-kafka-topics.sh (IP:PORT)"

# 128.31.25.127:9092
KAFKA=$1
echo "KAFKA: $KAFKA"

STORAGE_FILE=alltopics
# clear previous file

rm $STORAGE_FILE
# 1. read all kafka topics as list
./bin/kafka-topics.sh --bootstrap-server $KAFKA --list > $STORAGE_FILE
# 2. use a loop to clean every topics
topiclist=()
while IFS= read -r line; do
  if [ ! -z "$line" ]; then
    topiclist+=("$line")
  fi
done < $STORAGE_FILE

for topic in "${topiclist[@]}"
do
  if [ "$ip" != "__consumer_offsets" ]; then
    echo "deleting topic: $topic"
    ./bin/kafka-topics.sh --bootstrap-server "$KAFKA" --delete --topic "$topic"
  fi
done

# 3. remove alltopics
rm $STORAGE_FILE
