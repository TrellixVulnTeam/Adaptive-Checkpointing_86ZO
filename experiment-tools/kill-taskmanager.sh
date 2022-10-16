#!/bin/bash
USAGE="Usage: ./kill-taskmanager.sh KILL_TIME &"
KILL_TIME=$1
echo "kill the taskmanger after $KILL_TIME second"
# clear previous file
sleep "$KILL_TIME"
var=$(jps | grep TaskManagerRunner)
array=($var)
pid=${array[0]}
if [ ! -z "$pid" ]; then
  echo "pid is $pid"
  kill -9 "$pid"
fi
