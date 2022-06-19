#!/bin/bash
export FLINKROOT=$(cd ..; pwd)
echo $FLINKROOT

bin=`dirname "$0"`
bin=`cd "$bin"; pwd`
. "$bin"/config.sh
echo $bin

# build jar
cp all_pom_template.xml ../flink-examples/flink-examples-streaming/pom.xml
cd .. && mvn spotless:apply && mvn clean package -DskipTests

# move and rename to current folder
if [ ! -d  $TARGET_DIR ]; then
  mkdir "$TARGET_DIR"
else
  echo dir exist
fi
# a problem to resolve ?
sleep 5
cp "$FLINKROOT"/flink-examples/flink-examples-streaming/target/Query1-jar-with-dependencies.jar "$TARGET_DIR"/"$QUERY1".jar
cp "$FLINKROOT"/flink-examples/flink-examples-streaming/target/Query1-jar-with-dependencies.jar "$TARGET_DIR"/"$QUERY3".jar
cp "$FLINKROOT"/flink-examples/flink-examples-streaming/target/Query1-jar-with-dependencies.jar "$TARGET_DIR"/"$QUERY5".jar
cp "$FLINKROOT"/flink-examples/flink-examples-streaming/target/Query1-jar-with-dependencies.jar "$TARGET_DIR"/"$QUERY8".jar
cp "$FLINKROOT"/flink-examples/flink-examples-streaming/target/KafkaSourceBid-jar-with-dependencies.jar "$TARGET_DIR"/"$BID_SOURCE".jar
cp "$FLINKROOT"/flink-examples/flink-examples-streaming/target/KafkaSourceAuction-jar-with-dependencies.jar "$TARGET_DIR"/"$AUCTION_SOURCE".jar
cp "$FLINKROOT"/flink-examples/flink-examples-streaming/target/KafkaSourceBid-jar-with-dependencies.jar "$TARGET_DIR"/"$PERSON_SOURCE".jar
