#!/bin/bash
FLINKROOT=$(cd ..; pwd)
echo "FLINKROOT: $FLINKROOT"

bin=`dirname "$0"`
bin=`cd "$bin"; pwd`
. "$bin"/config.sh
echo "bin: $bin"

FOLDER_QUERY="queries"
FOLDER_KAFKA_SOURCE="kafkaSources"

JOB=$1
CURR_FOLDER=""
CURR_JOB=""
case $JOB in
     (1)
         CURR_JOB=$QUERY1
         CURR_FOLDER=$FOLDER_QUERY
     ;;
     (3)
         CURR_JOB=$QUERY3
         CURR_FOLDER=$FOLDER_QUERY
     ;;
     (5)
         CURR_JOB=$QUERY5
         CURR_FOLDER=$FOLDER_QUERY
     ;;
     (8)
         CURR_JOB=$QUERY8
         CURR_FOLDER=$FOLDER_QUERY
     ;;
     (a)
         CURR_JOB=$AUCTION_SOURCE
         CURR_FOLDER=$FOLDER_KAFKA_SOURCE
     ;;
     (b)
         CURR_JOB=$BID_SOURCE
         CURR_FOLDER=$FOLDER_KAFKA_SOURCE
     ;;
     (p)
         CURR_JOB=$PERSON_SOURCE
         CURR_FOLDER=$FOLDER_KAFKA_SOURCE
     ;;
     (*)
         echo "Unknown Query '${QUERY}'. $USAGE."
         exit 1
     ;;
esac

printf '%s %s\n' $CURR_FOLDER $CURR_JOB
sed 's/FOLDER/'"$CURR_FOLDER"'/g' ./pom_template.xml > ./pom.xml
# run on mac
#sed -i "" 's/QUERYNO/'"$CURR_JOB"'/g' ./pom.xml
# run on linux
sed -i 's/QUERYNO/'"$CURR_JOB"'/g' ./pom.xml


# build jar
cp pom.xml ../flink-examples/flink-examples-streaming/
rm ./pom.xml
cd .. && mvn spotless:apply && mvn clean package -DskipTests

# move and rename to current folder
if [ ! -d "$bin"/"$TARGET_DIR" ]; then
  mkdir "$bin"/"$TARGET_DIR"
else
  echo "dir exist"
fi
cp "$FLINKROOT"/flink-examples/flink-examples-streaming/target/flink-examples-streaming_2.11-1.14.0-jar-with-dependencies.jar "$bin"/"$TARGET_DIR"/"$CURR_JOB".jar
