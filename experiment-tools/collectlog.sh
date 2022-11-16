#!/bin/bash
FLINKROOT=$(cd ..; pwd)
echo $FLINKROOT

QUERY_ID=$1
EXP=$2

iplist=$(python3 get_sink_ip.py "$QUERY_ID")\

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
  echo "sink ip address: $ip"
  ifname="log"
  mkdir "$FLINKROOT"/experiment-tools/"$QUERY_ID"/"$ifname"
  scp "$ip":"$FLINKROOT"/flink-dist/target/flink-1.14.0-bin/flink-1.14.0/log/*.log "$FLINKROOT"/experiment-tools/"$QUERY_ID"/"$ifname"/

  if [ "$EXP" = "exp2" ] || [ "$EXP" = "EXP2" ]; then
    ifname="out"
    mkdir "$FLINKROOT"/experiment-tools/"$QUERY_ID"/"$ifname"
    scp "$ip":"$FLINKROOT"/flink-dist/target/flink-1.14.0-bin/flink-1.14.0/log/*.out "$FLINKROOT"/experiment-tools/"$QUERY_ID"/"$ifname"/
  fi
done

