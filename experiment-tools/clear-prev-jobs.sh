#!/bin/bash
# scp this file to kafka machine cd kafka/
# ssh to kafka machine and sh this file
USAGE="Usage: clear-prev-jobs.sh"

STORAGE_FILE=allprevjobs
# clear previous file

export FLINKROOT=$(cd ..; pwd)
echo $FLINKROOT
cd "$FLINKROOT"/flink-dist/target/flink-1.14.0-bin/flink-1.14.0/ || exit 1

rm $STORAGE_FILE
# 1. read all kafka jobs as list
./bin/flink list > $STORAGE_FILE & \
# 2. use a loop to clean every jobs
joblist=()
while IFS= read -r line; do
  job="$line"
  printf '%s\n' $job
  joblist+=("$line")
done < $STORAGE_FILE

for job in "${joblist[@]}"
do
  echo "$job"
  ./bin/flink cancel "$job" & \
done

# 3. remove alljobs
rm $STORAGE_FILE
