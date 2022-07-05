#!/bin/bash
export FLINKROOT=$(cd ..; pwd)
echo $FLINKROOT

QUERY_ID=$1
FETCH_TOTAL_TIME=$2
METRCIS_FETCH_INTERVAL=$3
echo "$QUERY_ID"
echo "$FETCH_TOTAL_TIME"
echo "$METRCIS_FETCH_INTERVAL"

cd "$FLINKROOT"/flink-dist/target/flink-1.14.0-bin/flink-1.14.0/conf || (echo cd fails && exit 1)
iplist=()
while IFS= read -r line; do
  ip="$line"
  iplist+=("$ip")
done < workers

cd "$FLINKROOT"/experiment-tools || (echo cd flink root fails && exit 1)
echo "========= connecting flink nodes for metrics ==========="
for ip in "${iplist[@]}"
do
  ssh "$ip" 'bash -s' < get-sys-metrics.sh "$QUERY_ID" "$FETCH_TOTAL_TIME" "$METRCIS_FETCH_INTERVAL" &
done
wait

echo "========= scp metrics files from flink nodes ==========="
cd "$FLINKROOT"/experiment-tools || (echo cd flink root fails && exit 1)
if [ -d "$QUERY_ID"/sys-metrics ]
  then rm -rf "$QUERY_ID"/sys-metrics
fi
mkdir "$QUERY_ID"/sys-metrics
for ip in "${iplist[@]}"
do
  scp -r "$ip":"$QUERY_ID"/ "$FLINKROOT"/experiment-tools/"$QUERY_ID"/sys-metrics/"$ip"
done

