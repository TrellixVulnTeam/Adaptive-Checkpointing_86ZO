#!/bin/bash
QUERY_ID=$1
FETCH_TOTAL_TIME=$2
METRICS_FETCH_INTERVAL=$3
REPEAT=`expr $FETCH_TOTAL_TIME / $METRICS_FETCH_INTERVAL`
count=1

var=$(jps | grep TaskManagerRunner)
array=($var)
pid=${array[0]}

if [ -d "$QUERY_ID"/sys-metrics ]
  then rm -rf "$QUERY_ID"/sys-metrics
fi
mkdir "$QUERY_ID"/sys-metrics

cd "$QUERY_ID"/sys-metrics || (echo cd fails && exit 1)
echo $pid
while(( $count <= $REPEAT))
do
  count=$(( $count + 1))
  sleep "$METRICS_FETCH_INTERVAL"
  thread_num=$(cat /proc/$pid/status | grep Threads)
  echo -e $thread_num >> thread_num_record.txt

done



