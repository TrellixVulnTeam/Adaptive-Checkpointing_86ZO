#!/bin/bash
export FLINKROOT=$(cd ..; pwd)
echo $FLINKROOT

QUERY_ID=$1
FETCH_TOTAL_TIME=$2
METRCIS_FETCH_INTERVAL=$3
echo "$QUERY_ID"
echo "$FETCH_TOTAL_TIME"
echo "$METRCIS_FETCH_INTERVAL"

echo "========= connecting flink nodes for metrics ==========="
ssh flinknode-2 'bash -s' < get-sys-metrics.sh "$FETCH_TOTAL_TIME" "$METRCIS_FETCH_INTERVAL" &
ssh flinknode-3 'bash -s' < get-sys-metrics.sh "$FETCH_TOTAL_TIME" "$METRCIS_FETCH_INTERVAL" &
wait

echo "========= scp metrics files from flink nodes ==========="
cd "$FLINKROOT"/flink-dist/target/flink-1.14.0-bin/flink-1.14.0/conf || (echo cd fails && exit 1)
iplist=()
while IFS= read -r line; do
  ip="$line"
  iplist+=("$line")
done < workers

for ip in $iplist
do
  scp "$ip":sys-metrics "$FLINKROOT"/experiment-tools/"$QUERY_ID"/
done
