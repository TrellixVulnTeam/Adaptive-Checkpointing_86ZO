#!/bin/bash
USAGE="Usage: ./kill-taskmanager.sh KILL_TIME &"
KILL_TIME=$1
echo "kill the taskmanger after $KILL_TIME second"
STORAGE_FILE=allprocess
# clear previous file
rm $STORAGE_FILE
sleep "$KILL_TIME"
jps > $STORAGE_FILE

while IFS= read -r line; do
  str=$line
  name="TaskManagerRunner"
  res=$(echo "$str" | grep "${name}")
  p=$( grep -o '[0-9]+' <<< "$str" )
  if [ ! -z "$res" ] && [ ! -z "$p" ] ; then
    echo "pid is $p"
    kill -9 "$p"
    break
  fi
done < $STORAGE_FILE
