#!/bin/bash
export FLINKROOT=$(cd ..; pwd)
echo $FLINKROOT
USAGE="Usage: start-exp.sh (1/3/5/8)"
KAFKAIP="128.31.25.127"
KAFKA="$KAFKAIP:9092"
JOBID_REGEX='[0-9a-fA-F]\{32\}'

bin=`dirname "$0"`
bin=`cd "$bin"; pwd`
echo $bin

# clean all previous jobs
. "$bin"/clear-prev-jobs.sh

# clean logs before a new experiment start
# rm "$FLINKROOT"/build-target/log/* will not clean taskmanagers' lgo, have to restart-cluster to clean log file
cd "$FLINKROOT"/deploy-scripts/ || (echo "cd fail" && exit 1)
. deployflink.sh
cd "$bin" || (echo "cd fail" && exit 1)

# clean all previous kafka topics
scp -r "$bin"/clear-kafka-topics.sh "ubuntu@$KAFKAIP":kafka/
ssh "ubuntu@$KAFKAIP" "cd kafka/ && ./clear-kafka-topics.sh $KAFKA"

# source config
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
echo  $QUERY_TO_RUN

# submit Query JOB
cd "$FLINKROOT"/flink-dist/target/flink-1.14.0-bin/flink-1.14.0/ || (echo cd fails && exit 1)

# Jobid storage
TEMP_JOBID_STORAGE="$bin"/getJobid
TEMP_BID_SOURCE_ID_STORAGE="$bin"/getBidSourceid
TEMP_AUCTION_SOURCE_ID_STORAGE="$bin"/getAuctionSourceid
TEMP_PERSON_SOURCE_ID_STORAGE="$bin"/getPersonSourceid
rm $TEMP_JOBID_STORAGE
rm $TEMP_BID_SOURCE_ID_STORAGE
rm $TEMP_AUCTION_SOURCE_ID_STORAGE
rm $TEMP_PERSON_SOURCE_ID_STORAGE
QUERY_ID=""

if [ $withTwoSource = true ]; then
    echo 2 Source

    Queryjar="$bin"/"$TARGET_DIR"/"$QUERY_TO_RUN.jar"
    auctionSjar="$bin"/"$TARGET_DIR"/"$AUCTION_SOURCE.jar"
    personSjar="$bin"/"$TARGET_DIR"/"$PERSON_SOURCE.jar"
    if [ ! -f  "$Queryjar" ] || [ ! -f  "$auctionSjar" ] || [ ! -f  "$personSjar" ] ; then
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

    sleep 5
    # run query
    ( ./bin/flink run --detached "$Queryjar" \
     --exchange-rate "$EXCHANGE_RAGE" \
     --checkpoint-dir "$CHECKPOINT_DIR" \
     --incremental-checkpoints "$INCREMENTAL_CHECKPOINTS" \
     --auction-kafka-topic "$AUCTION_TOPIC" \
     --auction-kafka-group "$GROUP" \
     --auction-broker "$KAFKA" \
     --person-kafka-topic "$PERSON_TOPIC" \
     --person-kafka-group "$GROUP" \
     --person-broker "$KAFKA"  & ) > "$TEMP_JOBID_STORAGE"

    # ensure query is setup before kafkasource
     while : ; do
         job=$( grep -o "$JOBID_REGEX" < "$TEMP_JOBID_STORAGE" )
         if [ ! -z "$job" ]; then
           printf 'Query JobID: %s\n' "$job"
           QUERY_ID=$job
           break;
         fi
     done

    # run auction source
    ( ./bin/flink run "$auctionSjar" \
     --kafka-topic "$AUCTION_TOPIC" \
     --broker "$KAFKA" \
     --ratelist "$RATELIST" & ) >  "$TEMP_AUCTION_SOURCE_ID_STORAGE"

    # ensure auction source is setup
    while : ; do
        job=$( grep -o "$JOBID_REGEX" < "$TEMP_AUCTION_SOURCE_ID_STORAGE" )
        if [ ! -z "$job" ]; then
          printf 'Auction Source JobID: %s\n' "$job"
          break;
        fi
    done

    # run person source
    ( ./bin/flink run "$personSjar" \
     --kafka-topic "$PERSON_TOPIC" \
     --broker "$KAFKA" \
     --ratelist "$RATELIST" & ) > "$TEMP_PERSON_SOURCE_ID_STORAGE"

    # ensure person source is setup
    while : ; do
        job=$( grep -o "$JOBID_REGEX" < "$TEMP_PERSON_SOURCE_ID_STORAGE" )
        if [ ! -z "$job" ]; then
          printf 'Auction Source JobID: %s\n' "$job"
          break;
        fi
    done

else
    Queryjar="$bin"/"$TARGET_DIR"/"$QUERY_TO_RUN.jar"
    bidSjar="$bin"/"$TARGET_DIR"/"$BID_SOURCE.jar"
    if [ ! -f  "$Queryjar" ] || [ ! -f  "$bidSjar" ] ; then
        echo "not enough jars"
        exit 1
    fi

    # create a new topic in kafka
    TIMESTAMP=$(date +%s)
    TOPICNAME='adaptive-checkpoint-'${TIMESTAMP}''
    printf 'kafkaip: bid topic_name: %s\n' "$TOPICNAME"
    ssh "ubuntu@$KAFKAIP" "cd kafka/ && bin/kafka-topics.sh --create --topic "$TOPICNAME" --bootstrap-server "$KAFKA""

    sleep 5
    # run query, & guaqi, \ huanhang, pid kill, chmod +x file
    ( ./bin/flink run --detached "$Queryjar" \
    --exchange-rate "$EXCHANGE_RAGE" \
    --checkpoint-dir "$CHECKPOINT_DIR" \
    --incremental-checkpoints "$INCREMENTAL_CHECKPOINTS" \
    --kafka-topic "$TOPICNAME" \
    --kafka-group "$GROUP" \
    --broker "$KAFKA" & ) > "$TEMP_JOBID_STORAGE"

    # ensure query is setup before kafkasource
     while : ; do
         job=$( grep -o "$JOBID_REGEX" < "$TEMP_JOBID_STORAGE" )
         if [ ! -z "$job" ]; then
           printf 'Query JobID: %s\n' "$job"
           QUERY_ID=$job
           break;
         fi
     done

    # run auction source
    ( ./bin/flink run "$bidSjar" \
     --kafka-topic "$TOPICNAME" \
     --broker "$KAFKA" \
     --ratelist "$RATELIST" & ) > "$TEMP_BID_SOURCE_ID_STORAGE"

    # ensure bid source is setup
     while : ; do
         job=$( grep -o "$JOBID_REGEX" < "$TEMP_BID_SOURCE_ID_STORAGE" )
         if [ ! -z "$job" ]; then
           printf 'Bod Source JobID: %s\n' "$job"
           break;
         fi
     done
fi

# start a timer to collect data here
echo "$QUERY_ID"
echo "$FETCH_INTERVAL"
echo "$FETCH_TOTAL_TIME"

# experiment end. collectlog.sh(need modification), mv all experiment data to QueryName + timestamp""

# clear all jobs and topics
