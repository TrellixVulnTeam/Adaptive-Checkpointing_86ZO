#!/bin/bash
# scp this file to kafka machine cd kafka/
# ssh to kafka machine and sh this file
USAGE="Usage: clear-prev-jobs.sh"

STORAGE_FILE=allprevjobs
# clear previous file

FLINKROOT=$(cd ..; pwd)
echo "FLINKROOT: $FLINKROOT"
FLINK_TARGET="$FLINKROOT"/flink-dist/target/flink-1.14.0-bin/flink-1.14.0

rm $STORAGE_FILE
# 1. read all jobs as list, avoid keep waiting when flink is not started
timeout 4 "$FLINK_TARGET"/bin/flink list & > "$STORAGE_FILE"
wait $!
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
  "$FLINK_TARGET"/bin/flink cancel "$job" &
done

# 3. remove alljobs
rm $STORAGE_FILE
