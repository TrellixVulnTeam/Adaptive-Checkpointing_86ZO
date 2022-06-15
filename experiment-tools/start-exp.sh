#!/bin/bash
export FLINKROOT=$(builtin cd ..; pwd)
echo $FLINKROOT
USAGE="Usage: start-exp.sh (1/3/5/8) (arg string)"
KAFAKIP="128.31.25.127"
QUERY1="Query1"
QUERY3="Query3Stateful"
QUERY5="Query5"
QUERY8="Query8"
BID_SOURCE="KafkaSourceBid"
AUCTION_SOURCE="KafkaSourceAuction"
PERSON_SOURCE="KafkaSourcePerson"

# create a new topic in kafka
TIMESTAMP=$(date +%s)
TOPICNAME='adaptive-checkpoint-'${TIMESTAMP}''
printf 'kafkaip: %s topic_name: %s\n' "$KAFKAIP" "$TOPICNAME"
ssh "ubuntu@$KAFKAIP" "cd kafka/ && bin/kafka-topics.sh --create --topic "$TOPICNAME" --bootstrap-server "$KAFKAIP":9092"

QUERY=$1
ARGSTR=$2
sourcelist=()
QUERY_TO_RUN=""

case $QUERY in
     (1)
          QUERY_TO_RUN=$Query1
          sourcelist+=("$KafkaSourceBid")
     ;;

     (3)
         QUERY_TO_RUN=$QUERY3
         sourcelist+=("$KafkaSourceAuction")
         sourcelist+=("$KafkaSourcePerson")
     ;;

     (5)
         QUERY_TO_RUN=$QUERY5
         sourcelist+=("$KafkaSourceBid")
     ;;

     (8)
         QUERY_TO_RUN=$QUERY8
         sourcelist+=("$KafkaSourceAuction")
         sourcelist+=("$KafkaSourcePerson")
     ;;
     (*)
         echo "Unknown Query '${QUERY}'. $USAGE."
         exit 1
     ;;
esac

target=`dirname "$0"`
echo $target
cd "$FLINKROOT"/flink-dist/target/flink-1.14.0-bin/flink-1.14.0/bin/
if [ "$QUERY_TO_RUN" = "$QUERY1" ] || [ "$QUERY_TO_RUN" = "$QUERY5" ]; then
    ./bin/flink run "$target"/target/"$QUERY_TO_RUN.jar"  --input ARGSTR
fi


