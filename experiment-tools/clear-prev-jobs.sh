#!/bin/bash
# scp this file to kafka machine cd kafka/
# ssh to kafka machine and sh this file
USAGE="Usage: clear-prev-jobs.sh"

STORAGE_FILE=allprevjobs
# clear previous file

export FLINKROOT=$(cd ..; pwd)
echo $FLINKROOT
cd "$FLINKROOT"/flink-dist/target/flink-1.14.0-bin/flink-1.14.0/ || (echo cd fails && exit 1)

rm $STORAGE_FILE
# 1. read all kafka jobs as list
./bin/flink list > "$STORAGE_FILE"
# 2. use a loop to clean every jobs
joblist=()
while IFS= read -r line; do
  job=$( grep -o '[0-9a-fA-F]\{32\}' <<< "$line" )
  if [ ! -z "$job" ]; then
    joblist+=("$job")
  fi
done < $STORAGE_FILE

for job in "${joblist[@]}"
do
  printf 'delete %s\n' $job
  ./bin/flink cancel "$job"
done

# 3. remove alljobs
rm $STORAGE_FILE
