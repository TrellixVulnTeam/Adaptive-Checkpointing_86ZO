#!/bin/bash
FLINKROOT=$(cd ..; pwd)
echo "FLINKROOT: $FLINKROOT"

bin=`dirname "$0"`
bin=`cd "$bin"; pwd`
. "$bin"/config.sh
echo "bin: $bin"

# build jar
cp all_pom_template.xml ../flink-examples/flink-examples-streaming/pom.xml
cd .. && mvn spotless:apply && mvn clean package -DskipTests

# move and rename to current folder
if [ ! -d  "$bin"/"$TARGET_DIR" ]; then
  mkdir "$bin"/"$TARGET_DIR"
else
  echo "dir exist"
fi
cp "$FLINKROOT"/flink-examples/flink-examples-streaming/target/Query1-jar-with-dependencies.jar "$bin"/"$TARGET_DIR"/"$QUERY1".jar
cp "$FLINKROOT"/flink-examples/flink-examples-streaming/target/Query3-jar-with-dependencies.jar "$bin"/"$TARGET_DIR"/"$QUERY3".jar
cp "$FLINKROOT"/flink-examples/flink-examples-streaming/target/Query5-jar-with-dependencies.jar "$bin"/"$TARGET_DIR"/"$QUERY5".jar
cp "$FLINKROOT"/flink-examples/flink-examples-streaming/target/Query8-jar-with-dependencies.jar "$bin"/"$TARGET_DIR"/"$QUERY8".jar
cp "$FLINKROOT"/flink-examples/flink-examples-streaming/target/KafkaSourceBid-jar-with-dependencies.jar "$bin"/"$TARGET_DIR"/"$BID_SOURCE".jar
cp "$FLINKROOT"/flink-examples/flink-examples-streaming/target/KafkaSourceAuction-jar-with-dependencies.jar "$bin"/"$TARGET_DIR"/"$AUCTION_SOURCE".jar
cp "$FLINKROOT"/flink-examples/flink-examples-streaming/target/KafkaSourcePerson-jar-with-dependencies.jar "$bin"/"$TARGET_DIR"/"$PERSON_SOURCE".jar

# home/ubuntu
NODE_ROOT=$(cd ~; pwd)
echo "NODE_ROOT: $NODE_ROOT"

# add hadoop pkg
cp $NODE_ROOT/commons-cli-1.5.0.jar  $FLINKROOT/build-target/lib/
cp $NODE_ROOT/flink-shaded-hadoop-3-uber-3.1.1.7.2.9.0-173-9.0.jar  $FLINKROOT/build-target/lib/

