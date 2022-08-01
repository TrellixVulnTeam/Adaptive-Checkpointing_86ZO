#!/bin/bash
QUERY_ID=$1
FETCH_TOTAL_TIME=$2
METRICS_FETCH_INTERVAL=$3
REPEAT=`expr $FETCH_TOTAL_TIME / $METRICS_FETCH_INTERVAL`
count=1

var=$(jps | grep TaskManagerRunner)
array=($var)
pid=${array[0]}

if [ -d "$QUERY_ID"/ ]
  then rm -rf "$QUERY_ID"/
fi
mkdir "$QUERY_ID"/
cd "$QUERY_ID"/ || (echo cd fails && exit 1)
echo $pid

get_threads_num(){
  thread_num=$(cat /proc/$pid/status | grep Threads)
  echo -e "$thread_num" >> thread_num_record.txt
}

get_cpu_usage(){
  usr_usage=$(top -b -n 1 | grep Cpu | awk '{print $2}')
#  sys_usage=$(top -b -n 1 | grep Cpu | awk '{print $4}')
#  cpu_usage=$( bc <<< "$us_usage + $sys_usage" )
  echo -e "$usr_usage" >> cpu_record.txt
}

while(( $count <= $REPEAT))
do
  count=$(( $count + 1))
  sleep "$METRICS_FETCH_INTERVAL"
#  get_threads_num $pid
  get_cpu_usage
#  get_disk_io $pid
done



