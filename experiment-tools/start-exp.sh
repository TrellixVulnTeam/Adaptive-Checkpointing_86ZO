#!/bin/bash
FLINKROOT=$(cd ..; pwd)
echo "FLINKROOT: $FLINKROOT"
USAGE="Usage: start-exp.sh (1/3/5/8)"
KAFKAIP="kafka" # if service starts on public ip write public ip here
KAFKA="$KAFKAIP:9092"
JOBID_REGEX='[0-9a-fA-F]\{32\}'

bin=`dirname "$0"`
bin=`cd "$bin"; pwd`
echo "bin: $bin"

# clean all hadoop files
. "$FLINKROOT"/hadoop-scripts/start-hdfs.sh

# clean all previous jobs
. "$bin"/clear-prev-jobs.sh

# clean logs before a new experiment start
# rm "$FLINKROOT"/build-target/log/* will not clean taskmanagers' lgo, have to restart-cluster to clean log file
. "$FLINKROOT"/deploy-scripts/deployflink.sh

# clean all previous kafka topics
scp -r "$bin"/clear-kafka-topics.sh "cc@$KAFKAIP":kafka/
ssh "cc@$KAFKAIP" "cd kafka/ && ./clear-kafka-topics.sh $KAFKA"

# source config
. "$bin"/config.sh
. "$bin"/argsconfig.sh
echo "CHECKPOINT_DIR: $CHECKPOINT_DIR"

QUERY=$1
DIR_PATH=$2
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
echo  "RUN QUERY: $QUERY_TO_RUN"

EXP_NAME="$EXP_TYPE"_"$QUERY_TO_RUN"_"$CKP_ADAPTER_RECOVERY"_"$CKP_ADAPTER_ALLOW_RANGE"_"$CKP_ADAPTER_CHECK_INTERVAL"
echo "EXP_NAME: $EXP_NAME"

# submit Query JOB
FLINK_TARGET="$FLINKROOT"/flink-dist/target/flink-1.14.0-bin/flink-1.14.0

# Jobid storage
TEMP_JOBID_STORAGE="$bin"/getJobid
TEMP_BID_SOURCE_ID_STORAGE="$bin"/getBidSourceid
TEMP_AUCTION_SOURCE_ID_STORAGE="$bin"/getAuctionSourceid
TEMP_PERSON_SOURCE_ID_STORAGE="$bin"/getPersonSourceid
rm "$TEMP_JOBID_STORAGE"
rm "$TEMP_BID_SOURCE_ID_STORAGE"
rm "$TEMP_AUCTION_SOURCE_ID_STORAGE"
rm "$TEMP_PERSON_SOURCE_ID_STORAGE"
QUERY_ID=""

if [ $withTwoSource = true ]; then
    echo "USE 2 SOURCE"

    Queryjar="$bin"/"$TARGET_DIR"/"$QUERY_TO_RUN.jar"
    auctionSjar="$bin"/"$TARGET_DIR"/"$AUCTION_SOURCE.jar"
    personSjar="$bin"/"$TARGET_DIR"/"$PERSON_SOURCE.jar"
    if [ ! -f  "$Queryjar" ] || [ ! -f  "$auctionSjar" ] || [ ! -f  "$personSjar" ] ; then
        echo "Not Enough Jars"
        exit 1
    fi

    # create first topic in kafka
    TIMESTAMP=$(date +%s)
    AUCTION_TOPIC='adaptive-checkpoint-'${TIMESTAMP}''
    printf 'kafkaip: auction topic_name: %s\n' "$AUCTION_TOPIC"
    ssh "cc@$KAFKAIP" "cd kafka/ && bin/kafka-topics.sh --create --topic "$AUCTION_TOPIC" --bootstrap-server "$KAFKA""

    # create second topic in kafka
    TIMESTAMP=$(date +%s)
    PERSON_TOPIC='adaptive-checkpoint-'${TIMESTAMP}''
    printf 'kafkaip: person topic_name: %s\n' "$PERSON_TOPIC"
    ssh "cc@$KAFKAIP" "cd kafka/ && bin/kafka-topics.sh --create --topic "$PERSON_TOPIC" --bootstrap-server "$KAFKA""

    GROUP_AUC="$GROUP-Auction"
    GROUP_PER="$GROUP-Person"

    sleep 2
    # run query
    ( "$FLINK_TARGET"/bin/flink run --detached "$Queryjar" \
     --exchange-rate "$EXCHANGE_RAGE" \
     --checkpoint-dir "$CHECKPOINT_DIR" \
     --incremental-checkpoints "$INCREMENTAL_CHECKPOINTS" \
     --ckp-interval "$CHECKPOINT_INTERVAL" \
     --ckp-adapter "$CKP_ADAPTER_RECOVERY" \
     --ckp-adapter-allow-range "$CKP_ADAPTER_ALLOW_RANGE" \
     --ckp-adapter-check-interval "$CKP_ADAPTER_CHECK_INTERVAL" \
     --ckp-adapter-inc-threshold "$CKP_ADAPTER_INC" \
     --ckp-adapter-dec-threshold "$CKP_ADAPTER_DEC" \
     --ckp-adapter-task-timer-interval "$CKP_ADAPTER_TASK_TIMER_INTERVAL" \
     --ckp-adapter-ema "$CKP_ADAPTER_EMA" \
     --ckp-adapter-counter-threshold "$CKP_ADAPTER_COUNTER" \
     --ckp-adapter-window "$CKP_ADAPTER_WINDOW" \
     --latency-marker "$LATENCY_MARKER_INTERVAL" \
     --auction-kafka-topic "$AUCTION_TOPIC" \
     --auction-kafka-group "$GROUP_AUC" \
     --auction-broker "$KAFKA" \
     --person-kafka-topic "$PERSON_TOPIC" \
     --person-kafka-group "$GROUP_PER" \
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
    ( "$FLINK_TARGET"/bin/flink run "$auctionSjar" \
     --kafka-topic "$AUCTION_TOPIC" \
     --broker "$KAFKA" \
     --ratelist "$AUCTION_RATELIST" & ) >  "$TEMP_AUCTION_SOURCE_ID_STORAGE"

    # ensure auction source is setup
    while : ; do
        job=$( grep -o "$JOBID_REGEX" < "$TEMP_AUCTION_SOURCE_ID_STORAGE" )
        if [ ! -z "$job" ]; then
          printf 'Auction Source JobID: %s\n' "$job"
          break;
        fi
    done

    # run person source
    ( "$FLINK_TARGET"/bin/flink run "$personSjar" \
     --kafka-topic "$PERSON_TOPIC" \
     --broker "$KAFKA" \
     --ratelist "$PERSON_RATELIST" & ) > "$TEMP_PERSON_SOURCE_ID_STORAGE"

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
        echo "Not Enough Jars"
        exit 1
    fi

    # create a new topic in kafka
    TIMESTAMP=$(date +%s)
    TOPICNAME='adaptive-checkpoint-'${TIMESTAMP}''
    printf 'kafkaip: bid topic_name: %s\n' "$TOPICNAME"
    ssh "cc@$KAFKAIP" "cd kafka/ && bin/kafka-topics.sh --create --topic "$TOPICNAME" --bootstrap-server "$KAFKA""

    sleep 2
    # run query, & guaqi, \ huanhang, pid kill, chmod +x file
    ( "$FLINK_TARGET"/bin/flink run --detached "$Queryjar" \
    --exchange-rate "$EXCHANGE_RAGE" \
    --checkpoint-dir "$CHECKPOINT_DIR" \
    --incremental-checkpoints "$INCREMENTAL_CHECKPOINTS" \
    --ckp-interval "$CHECKPOINT_INTERVAL" \
    --ckp-adapter "$CKP_ADAPTER_RECOVERY" \
    --ckp-adapter-allow-range "$CKP_ADAPTER_ALLOW_RANGE" \
    --ckp-adapter-check-interval "$CKP_ADAPTER_CHECK_INTERVAL" \
    --ckp-adapter-inc-threshold "$CKP_ADAPTER_INC" \
    --ckp-adapter-dec-threshold "$CKP_ADAPTER_DEC" \
    --ckp-adapter-task-timer-interval "$CKP_ADAPTER_TASK_TIMER_INTERVAL" \
    --ckp-adapter-ema "$CKP_ADAPTER_EMA" \
    --ckp-adapter-counter-threshold "$CKP_ADAPTER_COUNTER" \
    --ckp-adapter-window "$CKP_ADAPTER_WINDOW" \
    --latency-marker "$LATENCY_MARKER_INTERVAL" \
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

    # run bid source
    ( "$FLINK_TARGET"/bin/flink run "$bidSjar" \
     --kafka-topic "$TOPICNAME" \
     --broker "$KAFKA" \
     --ratelist "$BID_RATELIST" & ) > "$TEMP_BID_SOURCE_ID_STORAGE"

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
echo "QUERY_ID: $QUERY_ID"
echo "FETCH_INTERVAL: $FETCH_INTERVAL"
echo "FETCH_TOTAL_TIME: $FETCH_TOTAL_TIME"

echo "========= start collecting metrics ========="
cd "$FLINKROOT"/experiment-tools/ || (echo "cd fail" && exit 1)
python3 flink_connector.py --job_id "$QUERY_ID" --interval "$FETCH_INTERVAL" --total_time "$FETCH_TOTAL_TIME"
## collect system metrics
#. connect-for-metrics.sh "$QUERY_ID" "$FETCH_TOTAL_TIME" "$METRICS_FETCH_INTERVAL" &

# collect log
echo "========== start collecting logs =========="
. "$bin"/collectlog.sh "$QUERY_ID"
cd "$FLINKROOT"/experiment-tools/ || (echo "cd fail" && exit 1)
#
## collect all the files
#
python3 collect_data.py "$QUERY_ID" "$EXP_NAME" "$DIR_PATH"
#
## check if kill taskmanager
#
if $KILL_TASKMANAGER ;then
  (./kill-taskmanager.sh "$KILL_TIME") &
fi
#
# clear all jobs and topics
echo "=========== start clearing jobs and kafka topics ============="
cd "$FLINKROOT"/experiment-tools/ || (echo "cd fail" && exit 1)
. clear-prev-jobs.sh
cd "$FLINKROOT"/experiment-tools/ || (echo "cd fail" && exit 1)
. clear-kafka-topics.sh
