#!/bin/bash
export FLINKROOT=$(builtin cd ..; pwd)
echo $FLINKROOT
USAGE="Usage: start-exp.sh (1/3/5/8)"
KAFKAIP="128.31.25.127"
KAFAK="128.31.25.127:9092"

bin=`dirname "$0"`
bin=`cd "$bin"; pwd`
. "$bin"/config.sh
. "$bin"/argsconfig.sh

QUERY=$1
QUERY_TO_RUN=""
withTwoSource=false
case $QUERY in
     (1)
         QUERY_TO_RUN=$QUERY1
     ;;
     (3)
         QUERY_TO_RUN=$QUERY3
         withTwoSource=true
     ;;
     (5)
         QUERY_TO_RUN=$QUERY5
     ;;
     (8)
         QUERY_TO_RUN=$QUERY8
         withTwoSource=true
     ;;
     (*)
         echo "Unknown Query '${QUERY}'. $USAGE."
         exit 1
     ;;
esac

# submit Query JOB
cd "$FLINKROOT"/flink-dist/target/flink-1.14.0-bin/flink-1.14.0/ || echo cd fails && exit 1
if [ $withTwoSource = true ]; then
    echo 2 Source

    Queryjar="$bin"/"$TARGET_DIR"/"$QUERY_TO_RUN.jar"
    auctionSjar="$bin"/"$TARGET_DIR"/"$AUCTION_SOURCE.jar"
    personSjar="$bin"/"$TARGET_DIR"/"$PERSON_SOURCE.jar"
    if [ ! -f  $Queryjar ] || [ ! -f  $auctionSjar ] || [ ! -f  $personSjar ] ; then
        echo "not enough jars"
        exit 1
    fi

    # create first topic in kafka
    TIMESTAMP=$(date +%s)
    AUCTION_TOPIC='adaptive-checkpoint-'${TIMESTAMP}''
    printf 'kafkaip: auction topic_name: %s\n' "$AUCTION_TOPIC"
    ssh "ubuntu@$KAFKAIP" "cd kafka/ && bin/kafka-topics.sh --create --topic "$AUCTION_TOPIC" --bootstrap-server "$KAFKA""

    # create second topic in kafka
    TIMESTAMP=$(date +%s)
    PERSON_TOPIC='adaptive-checkpoint-'${TIMESTAMP}''
    printf 'kafkaip: person topic_name: %s\n' "$PERSON_TOPIC"
    ssh "ubuntu@$KAFKAIP" "cd kafka/ && bin/kafka-topics.sh --create --topic "$PERSON_TOPIC" --bootstrap-server "$KAFKA""

    # run query
    fork ./bin/flink run $Queryjar --auction-kafka-topic "$AUCTION_TOPIC" --auction-kafka-group "$GROUP" --auction-broker "$KAFKA" --person-kafka-topic "$PERSON_TOPIC" --person-kafka-group "$GROUP" --person-broker "$KAFKA"

    # run auction source
    fork ./bin/flink run $auctionSjar --kafka-topic "$TOPICNAME" --kafka-group "$GROUP" --broker "$KAFKA"

    # run person source
    fork ./bin/flink run $personSjar --kafka-topic "$TOPICNAME" --kafka-group "$GROUP" --broker "$KAFKA"

else
    Queryjar="$bin"/"$TARGET_DIR"/"$QUERY_TO_RUN.jar"
    bidSjar="$bin"/"$TARGET_DIR"/"$BID_SOURCE.jar"
    if [ ! -f  $Queryjar ] || [ ! -f  $bidSjar ] ; then
        echo "not enough jars"
        exit 1
    fi

    # create a new topic in kafka
    TIMESTAMP=$(date +%s)
    TOPICNAME='adaptive-checkpoint-'${TIMESTAMP}''
    printf 'kafkaip: bid topic_name: %s\n' "$TOPICNAME"
    ssh "ubuntu@$KAFKAIP" "cd kafka/ && bin/kafka-topics.sh --create --topic "$TOPICNAME" --bootstrap-server "$KAFKA""

    # run query
    fork ./bin/flink run $Queryjar --kafka-topic "$TOPICNAME" --kafka-group "$GROUP" --broker "$KAFKA"

    # run auction source
    fork ./bin/flink run $bidSjar --kafka-topic "$TOPICNAME" --kafka-group "$GROUP" --broker "$KAFKA"
fi


