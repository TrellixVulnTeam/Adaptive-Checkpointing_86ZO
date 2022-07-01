#!/bin/bash
export FLINKROOT=$(cd ..; pwd)
echo $FLINKROOT

iplist=$(python3 get_sink_ip.py)\
QUERY_ID=$1

cd "$FLINKROOT"/experiment-tools/"$QUERY_ID" || (echo "cd to job_id dir failed" && exit 1)

#mkdir "$FLINKROOT"/scripts/flinklogs_"$timestamp"/jobmaster
#cp "$FLINKROOT"/build-target/log/*  "$FLINKROOT"/scripts/flinklogs_"$timestamp"/jobmaster/

#while IFS= read -r line; do
#  ip="$line"
#  printf '%s\n' $ip
#  iplist+=("$line")
#done < workers

for ip in $iplist
do
  printf '%s\n' '-----------------------------------------------------'
  echo $ip
  ifname="${ip//\./\_}"
  echo $ifname
  mkdir "$FLINKROOT"/experiment-tools/"$QUERY_ID"/"$ifname"
  scp "$ip":"$FLINKROOT"/flink-dist/target/flink-1.14.0-bin/flink-1.14.0/log/*.log "$FLINKROOT"/scripts/flinklogs_"$timestamp"/"$ifname"/
done

